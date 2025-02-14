1. Install python 3.11
2. Install poetry
3. Install docker
4. Install `task` (sudo snap install task --classic)
5. Set up config.py (change env_file from .test.env to .prod.env)
6. Set up .prod.env
7. Execute in terminal `task build`

Use `task recreate` to recreate docker container when something changed
