from mesa import Agent, Model
from mesa.time import SimultaneousActivation
from mesa.space import MultiGrid
import random
import math

class CustomerAgent(Agent):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.time_entered_queue = self.model.schedule.time
        self.time_entered_service = None

    def step(self):
        
        if self.time_entered_service is None and self in self.model.queue:
            self.time_entered_service = self.model.schedule.time


class ServerAgent(Agent):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.customer_being_served = None
        self.next_completion_time = 0

    def step(self):
        
        if self.customer_being_served is None and len(self.model.queue) > 0:
            self.customer_being_served = self.model.queue.pop(0)
            self.customer_being_served.time_entered_service = self.model.schedule.time
            service_time = random.expovariate(1 / self.model.mean_service_time)
            self.next_completion_time = self.model.schedule.time + service_time

        # Si el servicio se ha completado, liberar el servidor.
        if self.model.schedule.time >= self.next_completion_time and self.customer_being_served:
            self.model.total_time_in_system += (self.model.schedule.time - self.customer_being_served.time_entered_queue)
            self.model.total_time_in_queue += (self.customer_being_served.time_entered_service - self.customer_being_served.time_entered_queue)
            self.model.total_system_throughput += 1
            self.customer_being_served = None

class QueueModel(Model):
   
    def __init__(self, mean_arrival_rate, mean_service_time, number_of_servers, max_ticks):
        self.mean_arrival_rate = mean_arrival_rate
        self.mean_service_time = mean_service_time
        self.number_of_servers = number_of_servers
        self.max_ticks = max_ticks
        self.schedule = SimultaneousActivation(self)
        self.grid = MultiGrid(10, 10, True) 
        self.queue = []
        
       
        self.total_time_in_queue = 0
        self.total_time_in_system = 0
        self.total_queue_throughput = 0
        self.total_system_throughput = 0
        
        
        for i in range(self.number_of_servers):
            server = ServerAgent(i, self)
            self.schedule.add(server)

    def step(self):
        
        if self.schedule.time < self.max_ticks:
            
            if random.random() < self.mean_arrival_rate:
                customer = CustomerAgent(self.total_queue_throughput, self)
                self.schedule.add(customer)
                self.queue.append(customer)
                self.total_queue_throughput += 1
            
            self.schedule.step()  

    def run_simulation(self):
        
        while self.schedule.time < self.max_ticks:
            self.step()

        
        avg_time_in_queue = self.total_time_in_queue / self.total_queue_throughput if self.total_queue_throughput > 0 else 0
        avg_time_in_system = self.total_time_in_system / self.total_system_throughput if self.total_system_throughput > 0 else 0
        avg_queue_length = self.total_time_in_queue / self.schedule.time if self.schedule.time > 0 else 0
        avg_servers_busy = sum([1 for server in self.schedule.agents if isinstance(server, ServerAgent) and server.customer_being_served is not None]) / self.schedule.time if self.schedule.time > 0 else 0

        return {
            'avg_time_in_queue': avg_time_in_queue,
            'avg_time_in_system': avg_time_in_system,
            'avg_queue_length': avg_queue_length,
            'avg_servers_busy': avg_servers_busy
        }

# Valores a modificar para lambda y miu a partir del calculo 
mean_arrival_rate = 1.0 
mean_service_time = 0.67
number_of_servers = 3    
max_ticks = 1000         


model = QueueModel(mean_arrival_rate, mean_service_time, number_of_servers, max_ticks)
model.run_simulation()


resultados = model.run_simulation()
print(resultados)
