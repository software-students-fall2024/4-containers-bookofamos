![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)
![ML-Client](https://github.com/software-students-fall2024/4-containers-bookofamos/actions/workflows/build-ml-client.yml/badge.svg)
![Web-App](https://github.com/software-students-fall2024/4-containers-bookofamos/actions/workflows/build-web-app.yml/badge.svg)

# Rock Paper Scissors

## Description
This project is designed to allow you to play Rock-Paper-Scissors with your hands via your webcam. Using machine learning, our app determines what gesture you are doing and then simulates a game against the computer. Additionally, we provide an in-depth statstics page to track your games.

## Authors
- [Dylan](https://github.com/dm6288)
- [Kevin](https://github.com/naruminato1)
- [Sean](https://github.com/bairixie)
- [Simon](https://github.com/simesherbs)

## Instructions
To build the image for the project simply run the command:
'''bash
docker-compose build
'''
Then to load the image, simple run:
'''bash
docker-compose up
'''
Alternatively, you can build and run in the the same command:
'''bash
docker-compose up --build
'''