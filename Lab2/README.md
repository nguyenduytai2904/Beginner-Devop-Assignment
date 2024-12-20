﻿# Lab2
## Create a CI/CD pipeline to deploy a Node.js application using GitHub Actions: https://github.com/arifsetiawan/node-test-sample. The pipeline should include:
  - Code linting and unit tests.
  - Building a Docker image of the application.
  - Deploying the Docker container to a local environment or cloud service.
  - Document the steps to set up and run the pipeline.
## Result each task
  - Code linting and unit tests
  ![image](https://github.com/user-attachments/assets/769195ec-87f1-4302-a4ff-1b212413122c)
  ![image](https://github.com/user-attachments/assets/67a3e4ab-732b-4017-9158-71c08b0fb427)
  - Building a Docker image of the application.
    ![image](https://github.com/user-attachments/assets/8e5e7922-6fa1-453a-90ed-3198658c32ed)
  - Deploying the Docker container to a local environment or cloud service.
    - Run with clone github project
        - Install NodeJs 20.x or higher 
    ```bash
    git clone https://github.com/nguyenduytai2904/Beginner-Devop-Assignment.git
    cd .\Lab2\
    npm ci
    npm run lint
    npm run test
    npm start
    ```
    - Run with docker
      - Install Docker
    ```bash
    docker pull nguyenduytai2904/node-test-sample:latest
    docker run nguyenduytai2904/node-test-sample:latest
    ```
  - Document the steps to set up and run the pipeline.
    
   
