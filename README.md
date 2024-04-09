# Code Generator Chat
![prompt: a team of futuristic AI agents working together to build an abstract product](CodeGeneratorChat.png?raw=true "Title")

## Overview
Code Generator Chat is an instruction-lead AI chat assistant designed to write code of 
any language and integrate with existing CI/CD pipelines with the goal of improving 
code generation accuracy beyond basic Q&A interaction with an LLM. 

This is achieved through a collaborative effort of specialized agents. 
Each agent within this ecosystem has a focused role just like in a classic team. 

By structuring a communication pipeline between agents, the team is able to break down 
a given task into smaller, more manageable parts and provide instructions or feedback 
to each other so that the final output is both validated to work but also meets all 
requirements given.

## Agents and Their Roles
The core agents include:

### Manager
The Manager agent acts as the central coordinator, orchestrating the operation of 
the other agents. It is responsible for ensuring that each agent contributes 
effectively according to their specialized function and that the structured sequence 
is adhered to without deviation.

[Manager Prompt](src/agents/prompts/manager.jinja)

### Planner
The Planner is the first agent in the sequence, responsible for receiving user input 
and outlining a strategic approach to the task at hand. This agent creates a blueprint 
that serves as the foundation for all subsequent actions.

[Planner Prompt](src/agents/prompts/planner.jinja)

### Programmer
Following the Planner, the Programmer translates the strategic blueprint into actionable 
code. This phase is critical and hinges entirely on the framework laid out by the Planner.

[Programmer Prompt](src/agents/prompts/programmer.jinja)


### Optimizer
The final step in the sequence involves the Optimizer, who reviews and refines the 
Programmer's code to ensure maximum efficiency and effectiveness. This agent's role is to 
provide a crucial layer of quality control, making it the last checkpoint in the task 
resolution process.

[Optimizer Prompt](src/agents/prompts/optimizer.jinja)

## Workflow Sequence
1. **Initiation**: Begins with the Planner, who sets the strategic foundation for the task.
2. **Development**: The Programmer then takes over, developing code based on the Planner's 
blueprint.
3. **Refinement**: Finally, the Optimizer reviews and enhances the code, focusing on 
efficiency and effectiveness.
4. **Finalization**: When the Optimizer concludes that no further improvements can be made, 
5. the session is terminated with the command `TERMINATE`.

# Deployment

## Install Requirements
```shell script
pip install -r requirements.txt
```
### Start Backend
```shell script
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Start Frontend
#### Change directory
```shell script
cd frontend
```

#### Install dependencies (assuming NPM and Node.js are installed)
```shell script
cd frontend
npm install 
npm run build
```
#### Start the frontend server
```shell script
npm run dev
```



# Examples:
- "Write a python function that finds all properties with a key of 'intf' within all nested child 
objects and return a list of all key value pairs that match. "

- "Write a python client that integrates with the [Vectara RAG API](https://docs.vectara.com/docs/). 
Use websockets for realtime updates of the query endpoint used in a user chat. 
The client will also need to lookup the corpus name using 'GET corpus' so the 
user can select the appropriate corpus for the chat. "

- "Write python unit tests that validates the functionality of the REST API 
endpoints in the following main.py file." <main.py attached>