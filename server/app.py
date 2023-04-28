#!/usr/bin/env python3

import os 
from flask import jsonify, make_response, request, session, g, current_app, redirect, abort
from flask_restful import Resource
import json
from sqlalchemy.exc import IntegrityError
from config import app,db,api
from models import User, Project, Task, File, Calendar, Team, Chat_Message
from flask_cors import CORS
CORS(app)

    ###########################################
    ##                Home API               ##
    ###########################################

class Home(Resource):
    def get(self):
        syntax_dict = '''
            <h1>"message": "Welcome to the Syntax Slingers RESTful API"</h1>
        '''
        response = make_response(syntax_dict, 200)
        return response
api.add_resource(Home, '/', endpoint='home')

    ###########################################
    ##            Logging in/Out             ##
    ##   Session, Authenticating, Password   ##
    ###########################################

# @app.before_request                 ## Commented out because it keeps giving me problems
# def check_if_logged_in():
#     access_list = ['home', 'clear', 'signup', 'check_session', 'login', ]
#     if (request.endpoint) not in access_list and (not session.get('user_id')):   
#         return {'error': 'Unauthorized'}, 401

class ClearSession(Resource):
    def delete(self):    
        session['user_id'] = None
        return {}, 204
api.add_resource(ClearSession, '/clear', endpoint='clear')  

class Signup(Resource):
    def post(self):
        username = request.get_json()['username']  
        password = request.get_json()['password']
        email = request.get_json()['email']
        if username and password:
            new_user = User(username=username, email=email, is_active=True, is_admin=False)
            new_user.password_hash = password
            try:
                db.session.add(new_user)
                db.session.commit()
                session['user_id'] = new_user.id
                return new_user.to_dict(), 201
            except IntegrityError:
                return {'error': '422 Unprocessable Entity'}, 422
        return {'error': '422 Unprocessable Entity'}, 422
api.add_resource(Signup, '/signup', endpoint='signup')

class CheckSession(Resource):
    def get(self):
        print(session)
        if session.get('user_id'):
            print(session['user_id'])
            user = User.query.filter(User.id == session.get('user_id')).first()
            return user.to_dict(), 200 
        return {'message': '401 Unauthorized'}, 401 
api.add_resource(CheckSession, '/check_session', endpoint='check_session')

class Login(Resource):
    def post(self):
        username = request.get_json()['username']
        password = request.get_json()['password']
        user = User.query.filter(User.username == username).first()
        if user:
            if user.authenticate(password):
                session['user_id'] = user.id
                return user.to_dict(), 200 
        return {'error': '401 Unauthorized'}, 401
api.add_resource(Login, '/login', endpoint='login')

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None
            return {'message': '204: No Content'}, 204
        return {'error': '401 Unauthorized'}, 401
api.add_resource(Logout, '/logout', endpoint='logout')

    ###########################################
    ##        GET, POST, PATCH, DELETE       ##
    ###########################################

##########
## USER ##
##########

class Users(Resource):          
    def get(self):
        try:
            user_dict_list = []
            for user in User.query.all(): 
                user_dict_list.append(user.to_dict())
            if user_dict_list != []:
                response = make_response(jsonify(user_dict_list), 200)
                return response
            else:
                return_obj = {"valid": False, "Reason": "Can't query User data"}                 
                return make_response(jsonify(return_obj),500)  
        except Exception as e:
            return make_response(jsonify({"errors": [e.__str__()]}), 422)

    def post(self):
        data=request.get_json()
        try:                                            
            new_user = User(
                username=data['username'], 
                email=data['email'],
                is_active=True,
                is_admin=False
                )
            new_user.password_hash = data['password'],
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            return make_response(jsonify({"errors": [e.__str__()]}), 422)
        user_dict = new_user.to_dict()
        response = make_response(jsonify(user_dict), 201) 
        return response 
    
api.add_resource(Users, '/users', endpoint='user')

class UserById(Resource):
    def get(self, id):
        try:
            user = User.query.filter(User.id == id).first()
            if user:
                user_dict = user.to_dict()
                response = make_response(jsonify(user_dict, 200))
                return response
            return make_response(jsonify({"error": "User Record not found"}), 404)
        except Exception as e:
            return make_response(jsonify({"errors": [e.__str__()]}), 422)

    def patch(self, id):
        try:
            user = User.query.filter(User.id == id).first()
            if user:
                data=request.get_json() 
                try:                                        
                    for attr in data:
                        setattr(user, attr, data[attr]) 
                    db.session.add(user) 
                    db.session.commit() 
                except Exception as e:
                    return make_response({"errors": [e.__str__()]}, 422)
                user_dict = user.to_dict()
                response = make_response(jsonify(user_dict), 201)
                return response 
            return make_response(jsonify({"error": "User Record not found"}), 404)
        except Exception as e:
            return make_response(jsonify({"errors": [e.__str__()]}), 422)

    def delete(self, id):
        try:
            user = User.query.filter(User.id == id).first()
            if user:
                db.session.delete(user)
                db.session.commit()
                user_dict = {"message": "User Record successfully deleted"}
                return make_response(user_dict, 200)
            return make_response(jsonify({"error": "User Record not found"}), 404)
        except Exception as e:
            return make_response(jsonify({"errors": [e.__str__()]}), 422)

api.add_resource(UserById, '/users/<int:id>', endpoint='userbyid')

#############
## PROJECT ##
#############

class Projects(Resource):
    def get(self):
        project_dict_list = []
        for project in Project.query.all():
            project_dict_list.append(project.to_dict())
        if project_dict_list != []:
            response = make_response(jsonify(project_dict_list), 200)
            return response
        else:
            return_obj = {"valid": False, "Reason": "Can't query Project data"}                 
            return make_response(jsonify(return_obj),500)  

    def post(self):
        data=request.get_json() 
        try:                                            
            new_project = Project(
                title=data['title'], 
                description=data['description'], 
                status=data['status'],
                start_date=data['start_date'],
                end_date=data['end_date'],
                team_id=int(data['team_id']),
                )
            db.session.add(new_project)
            db.session.commit()
        except Exception as e:
            return make_response(jsonify({"errors": [e.__str__()]}), 422)
        project_dict = new_project.to_dict()
        response = make_response(jsonify(project_dict), 201) 
        return response 

api.add_resource(Projects, '/projects', endpoint='project')

class ProjectById(Resource):
    def get(self, id): 
        project = Project.query.filter(Project.id == id).first()
        if project:
            project_dict = project.to_dict()
            response = make_response(jsonify(project_dict, 200))
            return response
        return make_response(jsonify({"error": "Project Record not found"}), 404)

    def patch(self, id):
        project = Project.query.filter(Project.id == id).first()
        if project:
            data=request.get_json() 
            try:                                        
                for attr in data: 
                    setattr(project, attr, data[attr])
                db.session.add(project) 
                db.session.commit() 
            except Exception as e:
                return make_response({"errors": [e.__str__()]}, 422)
            project_dict = project.to_dict()
            response = make_response(jsonify(project_dict), 201)
            return response 
        return make_response(jsonify({"error": "Project Record not found"}), 404)

    def delete(self, id):
        project = Project.query.filter(Project.id == id).first()
        if project:
            db.session.delete(project)
            db.session.commit()
            project_dict = {"message": "Project Record successfully deleted"}
            return make_response(project_dict, 200)
        return make_response(jsonify({"error": "Project Record not found"}), 404)

api.add_resource(ProjectById, '/projects/<int:id>', endpoint='projectbyid')

##########
## FILE ##
##########

class Files(Resource):
    def get(self):
        file_dict = []
        for file in File.query.all():
            file_dict.append(file.to_dict())
        if file_dict != []:
            response = make_response(jsonify(file_dict), 200)
            return response
        else:
            return_obj = {"valid": False, "Reason": "Can't query File data"}                 
            return make_response(jsonify(return_obj),500)  

    def post(self):
        data=request.get_json()
        try:                                            
            new_file = File(
                filename=data['filename'],
                file_type=data['file_type'],
                size=int(data['size']),
                date_uploaded=data['date_uploaded'],
                uploaded_by_user_id=int(data['uploaded_by_user_id']),
                project_id=int(data['project_id']),
                )
            db.session.add(new_file)
            db.session.commit()
        except Exception as e:
            return make_response(jsonify({"errors": [e.__str__()]}), 422)
        file_dict = new_file.to_dict()
        response = make_response(jsonify(file_dict), 201) 
        return response 

api.add_resource(Files, '/files', endpoint='file')

class FileById(Resource):
    def get(self, id):
        file = File.query.filter(File.id == id).first()
        if file:
            file_dict = file.to_dict()
            response = make_response(jsonify(file_dict, 200))
            return response
        return make_response(jsonify({"error": "File Record not found"}), 404)

    def patch(self, id):
        file = File.query.filter(File.id == id).first()
        if file:
            data=request.get_json() 
            try:                                        
                for attr in data:
                    setattr(file, attr, data[attr])
                db.session.add(file)
                db.session.commit() 
            except Exception as e:
                return make_response({"errors": [e.__str__()]}, 422)
            file_dict = file.to_dict()
            response = make_response(jsonify(file_dict), 201)
            return response 
        return make_response(jsonify({"error": "File Record not found"}), 404)

    def delete(self, id):
        file = File.query.filter(File.id == id).first()
        if file:
            db.session.delete(file)
            db.session.commit()
            file_dict = {"message": "File Record successfully deleted"}
            return make_response(file_dict, 200)
        return make_response(jsonify({"error": "File Record not found"}), 404)

api.add_resource(FileById, '/files/<int:id>', endpoint='filebyid')

##########
## TASK ##
##########

class Tasks(Resource):
    def get(self):
        task_dict_list = []
        for task in Task.query.all():
            task_dict_list.append(task.to_dict())
        if task_dict_list != []:
            response = make_response(jsonify(task_dict_list), 200)
            return response
        else:
            return_obj = {"valid": False, "Reason": "Can't query Task data"}                 
            return make_response(jsonify(return_obj),500)  

    def post(self):
        data=request.get_json()
        try:                                            
            new_task = Task(
                title=data['title'],
                description=data['description'],
                status=data['status'],
                due_date=data['due_date'],
                priority=int(data['priority']),
                assigned_to_user_id=int(data['assigned_to_user_id']),
                project_id=int(data['project_id']),
                )
            db.session.add(new_task)
            db.session.commit()
        except Exception as e:
            return make_response(jsonify({"errors": [e.__str__()]}), 422)
        task_dict = new_task.to_dict()
        response = make_response(jsonify(task_dict), 201) 
        return response 

api.add_resource(Tasks, '/tasks', endpoint='task')

class TaskById(Resource):
    def get(self, id):
        task = Task.query.filter(Task.id == id).first()
        if task:
            task_dict = task.to_dict()
            response = make_response(jsonify(task_dict, 200))
            return response
        return make_response(jsonify({"error": "Task Record not found"}), 404)

    def patch(self, id):
        task = Task.query.filter(Task.id == id).first()
        if task:
            data=request.get_json()
            try:                                        
                for attr in data:
                    setattr(task, attr, data[attr])
                db.session.add(task)
                db.session.commit()
            except Exception as e:
                return make_response({"errors": [e.__str__()]}, 422)
            task_dict = task.to_dict()
            response = make_response(jsonify(task_dict), 201)
            return response 
        return make_response(jsonify({"error": "Task Record not found"}), 404)

    def delete(self, id):
        task = Task.query.filter(Task.id == id).first()
        if task:
            db.session.delete(task)
            db.session.commit()
            task_dict = {"message": "Task Record successfully deleted"}
            return make_response(task_dict, 200)
        return make_response(jsonify({"error": "Task Record not found"}), 404)

api.add_resource(TaskById, '/tasks/<int:id>', endpoint='taskbyid')

##############
## CALENDAR ##
##############

class Calendars(Resource):
    def get(self):
        calendar_dict_list = []
        for calendar in Calendar.query.all():
            calendar_dict_list.append(calendar.to_dict())
        if calendar_dict_list != []:
            response = make_response(jsonify(calendar_dict_list), 200)
            return response
        else:
            return_obj = {"valid": False, "Reason": "Can't query Calendar data"}                 
            return make_response(jsonify(return_obj),500)  

    def post(self):
        data=request.get_json()
        try:                                            
            new_calendar = Calendar(
                event_name=data['event_name'],
                event_description=data['event_description'],
                event_date=data['event_date'],
                created_by_user_id=int(data['created_by_user_id']),
                )
            db.session.add(new_calendar)
            db.session.commit()
        except Exception as e:
            return make_response(jsonify({"errors": [e.__str__()]}), 422)
        calendar_dict = new_calendar.to_dict()
        response = make_response(jsonify(calendar_dict), 201) 
        return response 

api.add_resource(Calendars, '/calendars', endpoint='calendar')

class CalendarById(Resource):
    def get(self, id):
        calendar = Calendar.query.filter(Calendar.id == id).first()
        if calendar:
            calendar_dict = calendar.to_dict()
            response = make_response(jsonify(calendar_dict, 200))
            return response
        return make_response(jsonify({"error": "Calendar Record not found"}), 404)

    def patch(self, id):
        calendar = Calendar.query.filter(Calendar.id == id).first()
        if calendar:
            data=request.get_json()
            try:                                        
                for attr in data:
                    setattr(calendar, attr, data[attr])
                db.session.add(calendar)
                db.session.commit()
            except Exception as e:
                return make_response({"errors": [e.__str__()]}, 422)
            calendar_dict = calendar.to_dict()
            response = make_response(jsonify(calendar_dict), 201)
            return response 
        return make_response(jsonify({"error": "Calendar Record not found"}), 404)

    def delete(self, id):
        calendar = Calendar.query.filter(Calendar.id == id).first()
        if calendar:
            db.session.delete(calendar)
            db.session.commit()
            calendar_dict = {"message": "Calendar Record successfully deleted"}
            return make_response(calendar_dict, 200)
        return make_response(jsonify({"error": "Calendar Record not found"}), 404)

api.add_resource(CalendarById, '/calendars/<int:id>', endpoint='calendarbyid')

##########
## TEAM ##
##########

class Teams(Resource):
    def get(self):
        team_dict_list = []
        for team in Team.query.all():
            team_dict_list.append(team.to_dict())
        if team_dict_list != []:
            response = make_response(jsonify(team_dict_list), 200)
            return response
        else:
            return_obj = {"valid": False, "Reason": "Can't query Team data"}                 
            return make_response(jsonify(return_obj),500)  

    def post(self): 
        data=request.get_json() 
        try:                                            
            new_team = Team(
                name=data['name'], 
                description=data['description'], 
                date_created=data['date_created'],
                created_by_user_id=int(data['created_by_user_id']),
                )
            db.session.add(new_team)
            db.session.commit()
        except Exception as e:
            return make_response(jsonify({"errors": [e.__str__()]}), 422)
        team_dict = new_team.to_dict()
        response = make_response(jsonify(team_dict), 201) 
        return response 

api.add_resource(Teams, '/teams', endpoint='team')

class TeamById(Resource):
    def get(self, id): 
        team = Team.query.filter(Team.id == id).first()
        if team:
            team_dict = team.to_dict()
            response = make_response(jsonify(team_dict, 200))
            return response
        return make_response(jsonify({"error": "Team Record not found"}), 404)

    def patch(self, id):
        team = Team.query.filter(Team.id == id).first()
        if team:
            data=request.get_json() 
            try:                                        
                for attr in data: 
                    setattr(team, attr, data[attr])
                db.session.add(team) 
                db.session.commit() 
            except Exception as e:
                return make_response({"errors": [e.__str__()]}, 422)
            team_dict = team.to_dict()
            response = make_response(jsonify(team_dict), 201)
            return response 
        return make_response(jsonify({"error": "Team Record not found"}), 404)

    def delete(self, id): 
        team = Team.query.filter(Team.id == id).first()
        if team:
            db.session.delete(team)
            db.session.commit()
            team_dict = {"message": "Team Record successfully deleted"}
            return make_response(team_dict, 200)
        return make_response(jsonify({"error": "Team Record not found"}), 404)

api.add_resource(TeamById, '/teams/<int:id>', endpoint='teambyid')

##################
## Chat_Message ##
##################

class Chat_Messages(Resource):
    def get(self):     
        chat_message_dict = []
        for chat_message in Chat_Message.query.all():
            chat_message_dict.append(chat_message.to_dict())
        if chat_message_dict != []:
            response = make_response(jsonify(chat_message_dict), 200)
            return response
        else:
            return_obj = {"valid": False, "Reason": "Can't query Chat_Message data"}                 
            return make_response(jsonify(return_obj),500)  

    def post(self):  
        data=request.get_json()
        try:                                            
            new_chat_message = Chat_Message(
                message_text=data['message_text'],
                sender_user_id=int(data['sender_user_id']),
                receiver_user_id=int(data['receiver_user_id']),
                )
            db.session.add(new_chat_message)
            db.session.commit()
        except Exception as e:
            return make_response(jsonify({"errors": [e.__str__()]}), 422)
        chat_message_dict = new_chat_message.to_dict()
        response = make_response(jsonify(chat_message_dict), 201) 
        return response 

api.add_resource(Chat_Messages, '/chat_messages', endpoint='chat_message')

class Chat_MessageById(Resource):
    def get(self, id):
        chat_message = Chat_Message.query.filter(Chat_Message.id == id).first()
        if chat_message:
            chat_message_dict = chat_message.to_dict()
            response = make_response(jsonify(chat_message_dict, 200))
            return response
        return make_response(jsonify({"error": "Chat_Message Record not found"}), 404)

    def patch(self, id):          
        chat_message = Chat_Message.query.filter(Chat_Message.id == id).first()
        if chat_message:
            data=request.get_json() 
            try:                                        
                for attr in data:
                    setattr(chat_message, attr, data[attr])
                db.session.add(chat_message)
                db.session.commit() 
            except Exception as e:
                return make_response({"errors": [e.__str__()]}, 422)
            chat_message_dict = chat_message.to_dict()
            response = make_response(jsonify(chat_message_dict), 201)
            return response 
        return make_response(jsonify({"error": "Chat_Message Record not found"}), 404)

    def delete(self, id):         
        chat_message = Chat_Message.query.filter(Chat_Message.id == id).first()
        if chat_message:
            db.session.delete(chat_message)
            db.session.commit()
            chat_message_dict = {"message": "Chat_Message Record successfully deleted"}
            return make_response(chat_message_dict, 200)
        return make_response(jsonify({"error": "Chat_Message Record not found"}), 404)

api.add_resource(Chat_MessageById, '/chat_messages/<int:id>', endpoint='chat_messagebyid')

if __name__ == '__main__':
    app.run(port=5555, debug=True)