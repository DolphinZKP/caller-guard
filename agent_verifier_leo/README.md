# Caller Guard Leo Scripts

This directory contains Leo smart contracts for the Caller Guard application, specifically for minting and revoking agent information on the Aleo blockchain.

## Directory Structure

- `src/` - Source code for Leo programs
- `imports/` - External dependencies for Leo programs
- `inputs/` - Input files for testing Leo programs
- `outputs/` - Output files generated from program execution
- `build/` - Compiled artifacts

## Main Functions

The Leo program provides the following functionality:

1. `mint_agent` - Creates a new agent with a unique ID
2. `revoke_agent` - Revokes an existing agent

## Development

To build the program:

```bash
cd leo
leo build
```

To run the program with a test input:

```bash
leo run mint_agent
```

## Deployment

Once the program is finalized, compiled artifacts can be deployed to the Aleo blockchain.
