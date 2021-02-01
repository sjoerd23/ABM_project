# Covid Supermarket Model

## Structure
- ``agent.py`` implements the agent objects (customers and obstacles)
- ``CovidSupermarketModel.ipynb`` is used for interactive usage of the model and to do some analyzing
- ``data`` contains the input data of the model i.e. the layout of the supermarket
- ``model.py`` implements the model and contains the agents and the environment
- ``results`` contains the results of both OFAT and Sobol sensitivity analysis
- ``run.py`` used to activate and run the server
- ``server.py`` creates a server to animate the simulation
- ``space.py`` extends the mesa grid to offer extra utilities

## Usage
The model is developed using ``python3``. Usage is recommended with the latest ``python3`` and ``pip3`` versions

### Dependencies
All dependencies are located in requirements.txt. Install as follows:
```
    $ pip3 install -r requirements.txt
```
### Run model
To run the model with server animation (in the same directory as ``run.py``)
```
    $ mesa runserver
```

### Authors
Coen Prins *(11332441, coen_prins@hotmail.com)*</br>
Sjoerd Terpstra *(11251980, sjoerd.terpstra@student.uva.nl)*</br>
Kasper van Tulder *(11244011, kasper.vantulder@student.uva.nl)*
