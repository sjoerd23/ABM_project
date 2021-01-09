import model
from server import server

run_server = True

if run_server:
    server.launch()
else:
    width, height = 20, 20
    N_customers = 20
    model = model.CovidModel(N_customers, width, height)
    model.run_model(10)
