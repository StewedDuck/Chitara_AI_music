# Chitara AI Music – Domain Layer Implementation

## Overview
This project implements the core domain layer of an AI music generation system using Django.  
The system models how users create music generation requests, how songs are produced, and how related data such as parameters, sharing, and notifications are managed.

The focus of this implementation is on:
- data modeling
- relationships between entities
- persistent storage using Django ORM
- CRUD operations via Django Admin

---
## Setup Instructions

1. Clone the repository

```bash
git clone https://github.com/StewedDuck/Chitara_AI_music.git
cd Chitara_AI_music
```

2. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate   (Windows)
```

3. Install dependencies

```bash
pip install django
```

4. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create superuser

```bash
python manage.py createsuperuser
```

6. Run the development server

```bash
python manage.py runserver
```

7. Access admin panel

```bash
http://127.0.0.1:8000/admin
```

## System Design

The system is structured around the following core entities:

- **User**  
  Represents a system user who can create songs and receive notifications.

- **SongLibrary**  
  Each user has one personal library that stores their songs.

- **Song**  
  Represents a generated music track, including metadata such as title, duration, and status.

- **GenerationParameters**  
  Stores input configuration for music generation (genre, mood, voice type, prompt).

- **SongGenerationRequest**  
  Represents a request submitted by a user to generate a song.

- **SharedLink**  
  A unique link associated with a song for sharing.

- **Notification**  
  Messages sent to users about system events (e.g., song generation completed).

---

## Design Decisions

### GenerationParameters as a Separate Model
Generation parameters are stored as a separate entity instead of embedding them directly in Song.

Reason:
- allows reuse across multiple songs and requests
- avoids data duplication
- keeps the design modular

---

### Song Ownership and Library Relationship
Each Song is linked to:
- an owner (User)
- a library (SongLibrary)

Reason:
- owner is used for ownership and permission logic
- library is used for organizing songs
- system assumes consistency between owner and library

---

### SongGenerationRequest Flow
A SongGenerationRequest represents the process of generating a song.

In this implementation:
- requests are created manually through Django Admin
- a completed request is linked to a resulting Song

This simulates the generation workflow without integrating an actual AI service.

---

### SharedLink Design
Each Song is associated with exactly one SharedLink.

Reason:
- ensures a stable, unique link for sharing
- simplifies access to shared content

---

## Data Persistence

All entities are implemented using Django ORM and stored in a relational database.

Key features:
- automatic primary keys
- foreign key relationships
- one-to-one and one-to-many associations
- enforced constraints (e.g., unique email)

---

## CRUD Operations

CRUD functionality is provided through Django Admin:

- Create: add new records (users, songs, etc.)
- Read: view and list stored data
- Update: modify existing records
- Delete: remove records

The admin interface is used as a lightweight interface for interacting with the system.

## CRUD Functionality

CRUD operations are supported through Django Admin for all core entities.

### Create
New records can be created through the admin interface.
Examples:
- Creating a User
- Creating GenerationParameters
- Creating a Song linked to a User and SongLibrary

### Read
Stored data can be viewed through list and detail pages in the admin interface.
Examples:
- Viewing all songs in the system
- Viewing a user's library and related songs

### Update
Existing records can be modified through the admin edit interface.
Examples:
- Updating song title or status
- Changing parameters associated with a song

### Delete
Records can be removed through the admin delete function.
Examples:
- Deleting a Notification
- Removing a Song or GenerationRequest

All operations are persisted in the database using Django ORM.

---

## System Flow

The system supports the following workflow:

1. A user defines generation parameters  
2. A generation request is created  
3. A song is produced based on the request  
4. The song is stored in the user’s library  
5. A shareable link is generated  
6. The user receives a notification  

---

## Scope and Limitations

This implementation focuses only on the domain and data layer.

Not included:
- authentication system (e.g., OAuth)
- actual AI music generation
- frontend user interface

These components are intentionally excluded to keep the focus on core system modeling.

---

## Conclusion

The project demonstrates a structured and consistent domain model implemented using Django.  
It supports persistent data storage, clear entity relationships, and complete CRUD functionality through the admin interface.