# ai-Artifact-Provenance-Recorder
Records the build steps (commands, versions) that created an artifact. Outputs a JSON provenance file that can be used to verify the artifact's lineage. - Focused on Tools for generating, verifying, and managing the integrity of software artifacts (e.g., executables, scripts, configuration files). Focus on preventing supply chain attacks and unauthorized modifications by integrating hash comparison and digital signature verification into build/deployment processes.

## Install
`git clone https://github.com/ShadowStrikeHQ/ai-artifact-provenance-recorder`

## Usage
`./ai-artifact-provenance-recorder [params]`

## Parameters
- `--provenance_file`: No description provided
- `--command`: Command executed to build the artifact
- `--version`: Version of the tool used to build the artifact
- `--hash_algorithm`: No description provided

## License
Copyright (c) ShadowStrikeHQ
