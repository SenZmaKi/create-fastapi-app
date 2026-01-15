#!/usr/bin/env bash

# Load environment variables from .env file
# Only sets variables that are not already defined (manual args take precedence)
load_env() {
  local env_file="${1:-.env}"
  local script_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  local env_path="$script_root/$env_file"
  
  if [ -f "$env_path" ]; then
    # Read .env file and export variables that aren't already set
    while IFS='=' read -r key value || [ -n "$key" ]; do
      # Skip comments and empty lines
      [[ "$key" =~ ^[[:space:]]*# ]] && continue
      [[ -z "$key" ]] && continue
      
      # Remove leading/trailing whitespace from key
      key=$(echo "$key" | xargs)
      
      # Remove quotes from value if present
      value=$(echo "$value" | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")
      
      # Only export if variable is not already set
      if [ -z "${!key:-}" ]; then
        export "$key=$value"
      fi
    done < "$env_path"
  fi
}

# Parse command-line arguments to extract --testing flag and other arguments
# Sets global variables: TEST (true/false) and ARGS (array of remaining arguments)
parse_args() {
  TEST=false
  ARGS=()
  
  for arg in "$@"; do
    case "$arg" in
      --testing)
        TEST=true
        ;;
      *)
        ARGS+=("$arg")
        ;;
    esac
  done
}

# Run a command with ENV=testing if --testing flag was passed
# Usage: run_with_env <command> [args...]
run_with_env() {
  if [ "$TEST" = true ]; then
    ENV=testing "$@"
  else
    "$@"
  fi
}