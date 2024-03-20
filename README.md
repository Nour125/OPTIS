OPTIS is a standalone Python based web application which aims to minimize time requirements of busines processes. It's customized to work on a single business process, for which the user can get custom recommendations. To do that the OPTIS app uses a neural network trained with RL-techniques. The network can recommend the optimal next activity for any active case the user has in their event log.

To run the Docker image:

docker pull registry.github.com/Nour125/OPTIS

docker run -p 5000:5000 -d registry.github.com/Nour125/OPTIS
