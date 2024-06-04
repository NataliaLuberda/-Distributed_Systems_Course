# Medical Workflow Automation System

This project is a simulation of a medical workflow automation system using RabbitMQ. It demonstrates how doctors, technicians, and administrators can communicate and manage medical tasks effectively through a message broker. The system includes features for sending test orders, processing them, logging activities, and broadcasting administrative messages.

## Table of Contents

- [Components](#components)
- [Getting Started](#getting-started)
- [Running the Application](#running-the-application)
- [How the Application Works](#how-the-application-works)
- [Prerequisites](#prerequisites)
- [Contributing](#contributing)
- [License](#license)

## Components

The system consists of three main components:

1. **Doctor Module**
    - Allows doctors to send test orders for patients and receive results.
    - Receives administrative messages.
2. **Technician Module**
    - Processes test orders based on specified skills.
    - Sends test results to the requesting doctor.
    - Receives administrative messages.
3. **Administrator Module**
    - Logs all activities.
    - Broadcasts administrative messages to all users.

## Getting Started

### Prerequisites

- Python 3.x
- RabbitMQ server installed and running on your local machine

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/Distributed_Systems_Course.git
   cd Distributed_Systems_Course/MedicalWorkflowAutomation