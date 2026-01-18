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