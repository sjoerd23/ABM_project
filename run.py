import matplotlib.pyplot as plt
import numpy as np
import time
import model
from server import server


# set to true if you want to run the model through a server with visualisation. Run with: mesa runserver
# set to false if you don't want to run the server and like to analyze the data instead. Run with: python run.py
run_server = True

if run_server:
    server.launch()
