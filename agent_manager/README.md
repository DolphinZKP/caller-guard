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

## Other commands

leo execute mint_agent 424670554677936561047124518824635325114701728861320309810049233899774946975field 3004390782677111859190851561366000981442177319001004250798462378142068field

leo deploy --network testnet --endpoint "https://api.explorer.aleo.org/v1" --path . --dry-run
