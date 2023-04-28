#!/usr/bin/env python3

from datetime import datetime
from random import randint, choice as rc
from faker import Faker
from faker.providers.internet import *
from app import app
from models import db, User, Project, File, Team, Task, Calendar, Chat_Message

fake = Faker()

with app.app_context():

    print("Deleting User data...")
    User.query.delete()
    print("Deleting Team data...") 
    Team.query.delete()
    print("Deleting Project data...") 
    Project.query.delete()
    print("Deleting File data...")
    File.query.delete()
    print("Deleting Task data...") 
    Task.query.delete()
    print("Deleting Calendar data...") 
    Calendar.query.delete()
    print("Deleting Chat_Message data...") 
    Chat_Message.query.delete()

##########################################################

    print("Creating User data...")
    new_user_1 = User(username="Admin", email="Admin@flatironschool.com", is_active=True, is_admin=True)
    new_user_1.password_hash = "Admin"
    new_user_2 = User(username="Matthew", email="Matthew@flatironschool.com", is_active=False, is_admin=False)
    new_user_2.password_hash = "Matthew" 
    new_user_3 = User(username="Chris", email="Chris@flatironschool.com", is_active=False, is_admin=False)
    new_user_3.password_hash = "Chris"
    new_user_4 = User(username="Dylan", email="Dylan@flatironschool.com", is_active=False, is_admin=False)
    new_user_4.password_hash = "Dylan"
    new_user_5 = User(username="Jackie", email="Jackie@flatironschool.com", is_active=False, is_admin=False)
    new_user_5.password_hash = "Jackie"
    users = [new_user_1,new_user_2,new_user_3,new_user_4,new_user_5]
    usernames = ['Admin', 'Matthew', 'Chris', 'Dylan', 'Jackie']
    for n in range(20):
        username=fake.first_name()
        while username in usernames:
            username = fake.first_name()
        usernames.append(username)
        password = username
        new_user = User(username=username, email=fake.email(), is_active=False, is_admin=False)
        new_user.password_hash = password
        users.append(new_user)
    print('Adding User objects...')
    db.session.add_all(users)

##########################################################

    print("Creating Team data...")    
    team_1 = Team(
        name="Team 1",
        description="Team 1 is really awesome and smart",
        created_by_user_id=1,
    )
    team_2 = Team(
        name="Team 2",
        description="Team 2 is really awesome and smart",
        created_by_user_id=2,
    )
    team_3 = Team(
        name="Team 3",
        description="Team 3 is really awesome and smart",
        created_by_user_id=3,
    )
    team_4 = Team(
        name="Team 4",
        description="Team 4 is really awesome and smart",
        created_by_user_id=4,
    )
    team_5 = Team(
        name="Team 5",
        description="Team 5 is really awesome and smart",
        created_by_user_id=5,
    )
    teams = [team_1, team_2, team_3, team_4, team_5]
    for i in range(20):
        team = Team(
            name=f"{fake.word()}",
            description=f"{fake.sentence()}",
            created_by_user_id=randint(1, 25),
        )
        teams.append(team)
    print('Adding Team objects...')
    db.session.add_all(teams)

##########################################################

    print("Creating Project data...")
    # f"{fake.date()}"
    # start_date_str = "2023-04-23 19:14:25"
    # datetime_object_1 = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
    # end_date_str = "2023-05-12 19:14:25"
    # datetime_object_2 = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
    project_1 = Project(
        title="Project 1",
        description="Project 1 is super duper extra important!",
        status="In Progress",
        start_date = f"{fake.date()}", 
        end_date=f"{fake.date()}",
        team_id=1,
    )
    project_2 = Project(
        title="Project 2",
        description="Project 2 is super duper extra important!",
        status="In Progress",
        start_date =f"{fake.date()}", 
        end_date=f"{fake.date()}",
        team_id=2,
    )
    project_3 = Project(
        title="Project 3",
        description="Project 3 is super duper extra important!",
        status="In Progress",
        start_date =f"{fake.date()}", 
        end_date=f"{fake.date()}",
        team_id=3,
    )
    project_4 = Project(
        title="Project 4",
        description="Project 4 is super duper extra important!",
        status="In Progress",
        start_date =f"{fake.date()}", 
        end_date=f"{fake.date()}",
        team_id=4,
    )
    project_5 = Project(
        title="Project 5",
        description="Project 5 is super duper extra important!",
        status="In Progress",
        start_date =f"{fake.date()}", 
        end_date=f"{fake.date()}",
        team_id=5,
    )
    projects = [project_1, project_2, project_3, project_4, project_5]

    for i in range(10):
        project = Project(
            title=f"{fake.word()}",
            description=f"{fake.sentence()}",
            status="In Progress",
            start_date=f"{fake.date()}",
            end_date=f"{fake.date()}",
            team=rc(teams),
        )
        projects.append(project)
    print('Adding Project objects...')
    db.session.add_all(projects)

##########################################################

    print("Creating File data...")
    files = []
    file_types = ["jpeg", "txt", "mp4", "mp3", "doc", "js", "py", "sql"]
    for user in users:
        for n in range(randint(1, 30)):
            file = File(
                filename=f"{fake.word()}",
                file_type=rc(file_types),
                size=randint(1,500),
                uploaded_by_user_id=user.id,
                project=rc(projects))
            files.append(file)
    print('Adding File objects...')
    db.session.add_all(files)

##########################################################

    print("Creating Task data...")
    # due_date_str = "2023-05-12 19:14:25"
    # datetime_object_3 = datetime.strptime(due_date_str, "%Y-%m-%d %H:%M:%S")
    tasks = []
    for user in users:
        for n in range(randint(1, 30)):
            task = Task(
                title=f"{fake.word()}",
                description=f"{fake.sentence()}",
                status="In Progress",
                due_date=f"{fake.date()}",
                priority=randint(1,10),
                assigned_to_user_id=user.id,
                project=rc(projects)
                )
            tasks.append(task)
    print('Adding Task objects...')
    db.session.add_all(tasks)

##########################################################

    print("Creating Calendar) data...")
    # event_date_str = "2023-05-12 19:14:25"
    # datetime_object_4 = datetime.strptime(event_date_str, "%Y-%m-%d %H:%M:%S")
    new_event_1 = Calendar(event_name="Event 1", event_description= f"{fake.sentence()}", event_date=f"{fake.date()}")
    new_event_2 = Calendar(event_name="Event 2", event_description= f"{fake.sentence()}", event_date=f"{fake.date()}")
    new_event_3 = Calendar(event_name="Event 3", event_description= f"{fake.sentence()}", event_date=f"{fake.date()}")
    new_event_4 = Calendar(event_name="Event 4", event_description= f"{fake.sentence()}", event_date=f"{fake.date()}")
    new_event_5 = Calendar(event_name="Event 5", event_description= f"{fake.sentence()}", event_date=f"{fake.date()}")
    calendars = [new_event_1,new_event_2,new_event_3,new_event_4,new_event_5]
    event_names = ['Event 1', 'Event 2', 'Event 3', 'Event 4', 'Event 5']
    for n in range(20):
        event_name=f"Event_{fake.first_name()}"
        while event_name in event_names:
            event_name = f"Event_{fake.first_name()}"
        event_names.append(event_name)
        new_event = Calendar(event_name=event_name, event_description= f"{fake.sentence()}", event_date=f"{fake.date()}")
        calendars.append(new_event)
    print('Adding Calendar objects...')
    db.session.add_all(calendars)

##########################################################

    print("Creating Chat Message data...")
    chat_messages = []
    for user in users:
        for n in range(randint(1, 10)):
            chat_message = Chat_Message(
                message_text=f"{fake.sentence()}",
                sender_user_id=user.id,
                receiver_user_id=rc(users).id)
            chat_messages.append(chat_message)
    print('Adding Chat Message objects...')
    db.session.add_all(chat_messages)

##########################################################

    print("Just collating Data, as they say...")
    for project in projects:
        file= rc(files)
        project.file = file
        files.remove(file)
        task= rc(tasks)
        project.task = task
        tasks.remove(task)

    print('Committing Seed...')
    db.session.commit()

    print("Seeding Complete!")