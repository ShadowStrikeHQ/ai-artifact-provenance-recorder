import argparse
import hashlib
import json
import logging
import os
import subprocess
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ProvenanceRecorder:
    """
    Records the build steps (commands, versions) that created an artifact.
    Outputs a JSON provenance file that can be used to verify the artifact's lineage.
    """

    def __init__(self, artifact_path, provenance_file="provenance.json"):
        """
        Initializes the ProvenanceRecorder.

        Args:
            artifact_path (str): Path to the artifact to track.
            provenance_file (str): Name of the provenance file.
        """
        self.artifact_path = artifact_path
        self.provenance_file = provenance_file
        self.provenance_data = {
            "artifact": self.artifact_path,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "build_steps": [],
            "artifact_hash": None,
        }
        self.load_existing_provenance()

    def load_existing_provenance(self):
         """Loads existing provenance data if the file exists."""
         if os.path.exists(self.provenance_file):
            try:
                with open(self.provenance_file, 'r') as f:
                    self.provenance_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logging.warning(f"Could not load existing provenance file: {e}. Starting fresh.")


    def add_build_step(self, command, version=None):
        """
        Adds a build step to the provenance data.

        Args:
            command (str): The command that was executed.
            version (str, optional): The version of the tool used. Defaults to None.
        """
        try:
            step = {
                "command": command,
                "executed_at": datetime.utcnow().isoformat() + "Z",
            }
            if version:
                step["version"] = version
            self.provenance_data["build_steps"].append(step)
            logging.info(f"Added build step: {command}")
        except Exception as e:
            logging.error(f"Error adding build step: {e}")
            raise

    def calculate_hash(self, algorithm="sha256"):
        """
        Calculates the hash of the artifact.

        Args:
            algorithm (str): The hashing algorithm to use (e.g., "sha256", "sha512"). Defaults to "sha256".
        """
        try:
            if not os.path.exists(self.artifact_path):
                raise FileNotFoundError(f"Artifact not found: {self.artifact_path}")

            hasher = hashlib.new(algorithm)
            with open(self.artifact_path, "rb") as f:
                while chunk := f.read(4096):
                    hasher.update(chunk)

            self.provenance_data["artifact_hash"] = {
                "algorithm": algorithm,
                "hash": hasher.hexdigest(),
            }
            logging.info(f"Calculated {algorithm} hash: {self.provenance_data['artifact_hash']['hash']}")
        except FileNotFoundError as e:
            logging.error(f"File not found error: {e}")
            raise
        except Exception as e:
            logging.error(f"Error calculating hash: {e}")
            raise

    def save_provenance(self):
        """
        Saves the provenance data to a JSON file.
        """
        try:
            with open(self.provenance_file, "w") as f:
                json.dump(self.provenance_data, f, indent=4)
            logging.info(f"Provenance data saved to: {self.provenance_file}")
        except Exception as e:
            logging.error(f"Error saving provenance data: {e}")
            raise


def setup_argparse():
    """
    Sets up the argument parser.

    Returns:
        argparse.ArgumentParser: The argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Records the build steps and hash of an artifact for provenance tracking."
    )
    parser.add_argument("artifact_path", help="Path to the artifact")
    parser.add_argument(
        "--provenance_file",
        default="provenance.json",
        help="Name of the provenance file (default: provenance.json)",
    )
    parser.add_argument(
        "--command", help="Command executed to build the artifact"
    )
    parser.add_argument("--version", help="Version of the tool used to build the artifact")
    parser.add_argument(
        "--hash_algorithm",
        default="sha256",
        help="Hashing algorithm to use (default: sha256)",
    )
    return parser


def main():
    """
    Main function.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    try:
        # Input validation
        if not os.path.exists(args.artifact_path):
            raise FileNotFoundError(f"Artifact not found: {args.artifact_path}")

        recorder = ProvenanceRecorder(args.artifact_path, args.provenance_file)

        if args.command:
            recorder.add_build_step(args.command, args.version)

        recorder.calculate_hash(args.hash_algorithm)

        recorder.save_provenance()

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()