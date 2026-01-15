module.exports = {
  apps: [
    {
      name: "{{ app_name }}",
      cwd: "/var/www/{{ app_name }}",
      // Point the script directly to the python executable in your venv
      script: "./.venv/bin/python",
      // Pass the module flag and the module name as arguments
      args: "-m app",
      // Set the interpreter to none because we are calling the binary directly in 'script'
      interpreter: "none",
      watch: false,
      env: {
        PYTHONUNBUFFERED: "1",
        PYTHONPATH: "/var/www/{{ app_name }}",
      },
    },
  ],
};
