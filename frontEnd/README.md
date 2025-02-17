# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh


## Docker Setup
1. Install docker desktop from the links provided [Docker Desktop Installation](https://www.docker.com/products/docker-desktop/)

2. Under makefile, there are some commands where you can try to run backend seperately
    - docker-build: Allow you to build the docker image name as `frontendtest`
    - docker-run-test: Allow you to have a terminal for ease of debugging
    - docker-run: Allow you to execute the specific docker image