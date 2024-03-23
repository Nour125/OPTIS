OPTIS is a standalone Python-based web application that aims to minimize the time requirements of business processes. It's customized to work on a single business process, for which the user can get custom recommendations. To do that the OPTIS app uses a neural network trained with RL techniques. The network can recommend the optimal next activity for any active case the user has in their event log.

![RL_illustration|100](https://github.com/Nour125/OPTIS/assets/73433351/2911f8d2-acfa-4bd2-b0a2-ec7b4d22d86c)


To run the Docker image:

docker pull registry.github.com/Nour125/OPTIS

docker run -p 5000:5000 -d registry.github.com/Nour125/OPTIS
