#!/usr/bin/env python3
"""
Repo ingestion with gitingest + local clone.

This script:
  1. Runs gitingest and saves the structured repo text into gitingest_outputs/.
  2. Clones the repo locally into my_repos/owner/repo/.
"""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging
import shutil
import re
import stat
from flask import Flask, request, jsonify

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

def handle_remove_readonly(func, path, exc):
    # Clear the readonly flag and retry
    os.chmod(path, stat.S_IWRITE)
    func(path)


class RepoIngestor:
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token

    # ------------------------------
    # Utility: parse repo url
    # ------------------------------
    def parse_github_url(self, url: str):
        """Extract owner and repo from GitHub URL."""
        match = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$", url)
        if not match:
            raise ValueError(f"Invalid GitHub URL: {url}")
        return match.group("owner"), match.group("repo")

    # ------------------------------
    # Local cloning
    # ------------------------------
    def clone_repo(self, url: str, target_dir="my_repos", fresh=True):
        """
        Clone GitHub repo locally under my_repos/owner/repo.
        If fresh=True, delete old copy before cloning.
        """
        owner, repo = self.parse_github_url(url)
        repo_path = Path(target_dir) / owner / repo

        if fresh and repo_path.exists():
            logger.info(f"Removing old repo at {repo_path}")
            shutil.rmtree(repo_path, onerror=handle_remove_readonly)

        repo_path.parent.mkdir(parents=True, exist_ok=True)

        # Use token if provided
        clone_url = url
        if self.github_token and "@" not in url:
            clone_url = url.replace("https://", f"https://{self.github_token}@")

        logger.info(f"Cloning {owner}/{repo} into {repo_path}")
        result = subprocess.run(
            ["git", "clone", "--depth", "1", clone_url, str(repo_path)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"Git clone failed: {result.stderr.strip()}")

        logger.info(f"Cloned {owner}/{repo} successfully")
        return str(repo_path)

    # ------------------------------
    # Run gitingest
    # ------------------------------
    def  run_gitingest(self, repo_input: str, output_file: str) -> Dict[str, Any]:
        """Run gitingest and return structured text."""
        temp_file = None
        try:
            if not output_file:
                fd, temp_file = tempfile.mkstemp(suffix='.txt', prefix='gitingest_')
                os.close(fd)
                output_file = temp_file

            cmd = ["gitingest", repo_input, "--output", output_file]
            if self.github_token and not os.path.isdir(repo_input):
                cmd.extend(["--token", self.github_token])

            env = os.environ.copy()
            if self.github_token and not os.path.isdir(repo_input):
                env["GITHUB_TOKEN"] = self.github_token

            logger.info(f"Running gitingest on {repo_input}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                env=env,
                encoding="utf-8",
                errors="replace"
            )

            if result.returncode != 0:
                return {"success": False, "error": result.stderr.strip(), "repo_input": repo_input}

            with open(output_file, "r", encoding="utf-8", errors="replace") as f:
                structured_text = f.read()

            return {"success": True, "structured_text": "File Successfully Ingested!", "repo_input": repo_input}

        except Exception as e:
            return {"success": False, "error": str(e), "repo_input": repo_input}
        finally:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

    # ------------------------------
    # Check if repo index exists (chunks, graph, vectors)
    # ------------------------------
    def repo_index_exists(self, repo: str, indexes_dir="indexes"):
        """
        Check if all index files exist for this repo in indexes/{repo}/.
        """
        repo_dir = Path(indexes_dir) / repo
        return all([
            (repo_dir / "repo.index").exists(),
            (repo_dir / "chunks.json").exists(),
            (repo_dir / "graph.pkl").exists()
        ])

    # ------------------------------
    # Delete repo index folder
    # ------------------------------
    def delete_repo_index(self, repo: str, indexes_dir="indexes"):
        repo_dir = Path(indexes_dir) / repo
        if repo_dir.exists():
            logger.info(f"Deleting index folder: {repo_dir}")
            shutil.rmtree(repo_dir, onerror=handle_remove_readonly)
            return True
        return False

    # ------------------------------
    # Helpers to detect URL vs local path
    # ------------------------------
    def _is_probable_git_url(self, s: str) -> bool:
        s = (s or "").strip()
        return bool(re.match(r"^(https?://|git@|ssh://)", s)) or "github.com" in s

    def _normalize_local_path(self, s: str) -> str:
        p = (s or "").strip().strip('"').strip("'")
        p = os.path.expanduser(p)
        p = os.path.expandvars(p)
        return str(Path(p))

    # ------------------------------
    # High level API
    # ------------------------------
    def ingest_repo(self, repo_input: str, output_dir="gitingest_outputs", clone=True, indexes_dir="indexes") -> Dict[str, Any]:
        """Save gitingest output and optionally clone repo locally. Also checks and deletes existing index data."""
        Path(output_dir).mkdir(exist_ok=True)

        # Sanitize input
        if not repo_input or not str(repo_input).strip():
            return {"success": False, "error": "No repository URL or local path provided."}
        raw_input = str(repo_input).strip()

        is_url = self._is_probable_git_url(raw_input)
        owner = None
        repo = None

        if not is_url:
            # Treat as local path; require it to exist
            local_path = self._normalize_local_path(raw_input)
            if not os.path.isdir(local_path):
                return {"success": False, "error": f"Local path not found or not a directory: {local_path}"}
            repo_path = Path(local_path).resolve()
            owner = "Local"
            repo = repo_path.name

            # Save the local repository path in a .txt file under my_repos/Local/<repo_name>/repopath.txt
            local_repo_dir = Path("my_repos") / owner / repo
            local_repo_dir.mkdir(parents=True, exist_ok=True)
            local_repo_file = local_repo_dir / "repopath.txt"
            with open(local_repo_file, "w", encoding="utf-8") as f:
                f.write(str(repo_path))

            effective_input = str(repo_path)
        else:
            # Git URL
            owner, repo = self.parse_github_url(raw_input)
            effective_input = raw_input

        # Check and delete existing index data if present
        if self.repo_index_exists(repo, indexes_dir=indexes_dir):
            self.delete_repo_index(repo, indexes_dir=indexes_dir)

        timestamp = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{output_dir}/{owner}_{repo}_{timestamp}.txt"

        # Run gitingest (for URL or local path)
        result = self.run_gitingest(effective_input, output_file)
        if not result.get("success"):
            return result

        result["output_file"] = output_file
        logger.info(f"Structured output saved: {output_file}")

        # Clone only for URL inputs
        if clone and is_url and not os.path.isdir(effective_input):
            try:
                local_path = self.clone_repo(effective_input)
                result["local_repo"] = local_path
            except Exception as e:
                logger.warning(f"Repo clone skipped: {e}")
                result["local_repo"] = None

        return result


# ------------------------------
# CLI for testing
# ------------------------------
def prompt_repo_input() -> tuple[str, str | None]:
    print("\nSelect input type:")
    print("  [1] Git URL (e.g., https://github.com/owner/repo.git)")
    print("  [2] Local repo path (e.g., C:\\dev\\myproject)")
    choice = input("Enter 1 or 2: ").strip()
    while choice not in {"1", "2"}:
        choice = input("Please enter 1 or 2: ").strip()

    if choice == "1":
        url = input("Enter Git repo URL: ").strip()
        token = input("Enter GitHub token (leave blank if not needed): ").strip() or None
        return url, token

    while True:
        path = input("Enter local repo path: ").strip().strip('"').strip("'")
        path = os.path.expanduser(path)
        if os.path.isdir(path):
            return path, None
        print(f"Path not found or not a directory: {path}. Try again.\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest a repo from URL or local path")
    parser.add_argument("--repo", help="Git URL or local path to repo")
    parser.add_argument("--token", help="GitHub token for private repos (optional)")
    args = parser.parse_args()

    if args.repo:
        # Non-interactive mode (no prompts)
        processor = RepoIngestor(github_token=args.token or None)
        result = processor.ingest_repo(args.repo)
        print("\nIngest result:")
        print(result)
    else:
        # Interactive mode (prompts user for input)
        repo_input, token = prompt_repo_input()
        processor = RepoIngestor(github_token=token)
        result = processor.ingest_repo(repo_input)
        print("\nIngest result:")


@app.route('/ingest', methods=['POST'])
def ingest_repo():
    try:
        data = request.get_json()
        repo_link = data.get('repo_link')
        github_token = data.get('github_token') or None
        processor = RepoIngestor(github_token=github_token)
        result = processor.ingest_repo(repo_link)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
