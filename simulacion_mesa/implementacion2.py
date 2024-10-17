from mesa import Agent, Model
from mesa.time import SimultaneousActivation
from mesa.space import MultiGrid
import random

class Client(Agent):
    
    
    def __init__(self, client_id, model):
        super().__init__(client_id, model)
        self.queue_entry_time = self.model.schedule.time
        self.service_start_time = None

    def step(self):
       
        if self.service_start_time is None and self in self.model.queue:
            self.service_start_time = self.model.schedule.time


class Server(Agent):
    
    
    def __init__(self, server_id, model):
        super().__init__(server_id, model)
        self.active_customer = None
        self.completion_time = 0

    def step(self):
        
        if self.active_customer is None and self.model.queue:
            self.active_customer = self.model.queue.pop(0)
            self.active_customer.service_start_time = self.model.schedule.time
            service_duration = random.expovariate(1 / self.model.mean_service_time)
            self.completion_time = self.model.schedule.time + service_duration

       
        if self.model.schedule.time >= self.completion_time and self.active_customer:
            self.model.total_time_system += (self.model.schedule.time - self.active_customer.queue_entry_time)
            self.model.total_time_queue += (self.active_customer.service_start_time - self.active_customer.queue_entry_time)
            self.model.throughput += 1
            self.active_customer = None


class QueueSimulation(Model):
    #aqui es donde entra la logica para el modelo de M/M/n 
    
    def __init__(self, arrival_rate, service_time, num_servers, max_steps):
        self.mean_arrival_rate = arrival_rate
        self.mean_service_time = service_time
        self.num_servers = num_servers
        self.max_steps = max_steps
        self.schedule = SimultaneousActivation(self)
        self.grid = MultiGrid(10, 10, True)
        self.queue = []
        
        
        self.total_time_queue = 0
        self.total_time_system = 0
        self.throughput = 0
        
        
        for i in range(self.num_servers):
            self.schedule.add(Server(i, self))

    def step(self):
        
        if self.schedule.time < self.max_steps:
            
            if random.random() < self.mean_arrival_rate:
                client = Client(self.throughput, self)
                self.schedule.add(client)
                self.queue.append(client)
                self.throughput += 1
            
            self.schedule.step()  

    def run(self):
        
        while self.schedule.time < self.max_steps:
            self.step()

        
        avg_queue_time = self.total_time_queue / self.throughput if self.throughput > 0 else 0
        avg_system_time = self.total_time_system / self.throughput if self.throughput > 0 else 0
        avg_queue_length = self.total_time_queue / self.schedule.time if self.schedule.time > 0 else 0
        avg_servers_busy = sum(1 for server in self.schedule.agents if isinstance(server, Server) and server.active_customer is not None) / self.schedule.time if self.schedule.time > 0 else 0

        return {
            'avg_queue_time': avg_queue_time,
            'avg_system_time': avg_system_time,
            'avg_queue_length': avg_queue_length,
            'avg_servers_busy': avg_servers_busy
        }

#  Estos son los valores a cambiar para jugar con Lambda y Miu 
arrival_rate = 1.0  
service_time = 0.67  
num_servers = 3      
max_steps = 1000     


simulation_model = QueueSimulation(arrival_rate, service_time, num_servers, max_steps)
results = simulation_model.run()


print(results)
