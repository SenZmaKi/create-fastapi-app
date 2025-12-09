#!/usr/bin/env bash

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