from sqlalchemy.orm import validates, backref, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property
from config import bcrypt,db

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_rules = ('-tasks.user', '-files.user', '-teams.user', 'calendars.user', 'chat_messages.user',)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, server_default=db.func.now())
    last_login = db.Column(db.DateTime, onupdate=db.func.now())
    is_active = db.Column(db.Boolean)
    is_admin = db.Column(db.Boolean)

    tasks = db.relationship('Task', backref='user', cascade="all, delete, delete-orphan")
    files = db.relationship('File', backref='user', cascade="all, delete, delete-orphan")
    teams = db.relationship('Team', backref='user', cascade="all, delete, delete-orphan")
    calendars = db.relationship('Calendar', backref='user', cascade="all, delete, delete-orphan")
    sent_messages = db.relationship('Chat_Message', foreign_keys='Chat_Message.sender_user_id', cascade="all, delete, delete-orphan", overlaps='received_messages')
    received_messages = db.relationship('Chat_Message', foreign_keys='Chat_Message.receiver_user_id', cascade="all, delete, delete-orphan", overlaps='sent_messages')

    projects = association_proxy('tasks', 'project')
    projects = association_proxy('files', 'project')

    @hybrid_property
    def password_hash(self):
        raise Exception('Password hashes may not be viewed.')

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8')) 
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8'))

    @validates('username')
    def validate_username(self, key, username):
        users = User.query.all()
        usernames = [user.username for user in users]
        if not username:
            raise ValueError("User must have a username")
        elif username in usernames:
            raise ValueError("User Username must be unique")
        return username

    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise ValueError("User must have a email")
        if '@' not in email:
            raise ValueError("User failed simple email validation")
        return email
    
    def __repr__(self):
        return f'User ID: {self.id}, Username: {self.username}, Email: {self.email}, Date Created: {self.date_created}, Last Login: {self.last_login}, Is Admin: {self.is_admin}, Is Active: {self.is_active}>'

class Project(db.Model, SerializerMixin):
    __tablename__ = 'projects'

    serialize_rules = ('-tasks.project', '-files.project', '-teams.project', '-created_at', '-updated_at',)

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, db.CheckConstraint('len(description) <= 250', name='max_project_description_length'))
    status = db.Column(db.String, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    
    tasks = db.relationship('Task', backref='project', cascade="all, delete, delete-orphan")
    files = db.relationship('File', backref='project', cascade="all, delete, delete-orphan")
    users = association_proxy('tasks', 'user')
    users = association_proxy('files', 'user')
    
    @validates('title')
    def validate_project_title(self, key, title):
        projects = Project.query.all()
        project_titles = [project.title for project in projects]
        if not title:
            raise ValueError("Project must have a Title")
        elif title in project_titles:
            raise ValueError("Project Title must be unique")
        return title

    @validates('description')
    def validate_project_description_length(self, key, description):
        if not description:
            raise ValueError("Project must have a Description")
        if len(description) >= 250:
            raise ValueError("Project Description must be less than or equal to 250 characters long.")
        return description
    
    @validates('status')
    def validate_project_status(self, key, status):
        if not status:
            raise ValueError("Project must have a Status")
        return status
    
    @validates('start_date')
    def validate_project_start_date(self, key, start_date):
        if not start_date:
            raise ValueError("Project must have a Start Date")
        return start_date

    @validates('end_date')
    def validate_project_end_date(self, key, end_date):
        if not end_date:
            raise ValueError("Project must have an End Date")
        return end_date
    
    @validates('team_id')
    def validate_team_id(self, key, team_id):
        teams = Team.query.all()
        ids = [team.id for team in teams]
        if not team_id:
            raise ValueError("Project must have a team_id")
        elif int(team_id) not in ids:
            raise ValueError('Project Team must exist.')
        return team_id
    
    def __repr__(self):
        return f'<Project #{self.id}, Project Title: {self.title}, Project Description: {self.description}, Project Status: {self.status}, Project Start Date: {self.start_date}, Project End Date: {self.end_date}, Project team: {self.team.name}>'

class Task(db.Model, SerializerMixin): 
    __tablename__ = 'tasks'

    serialize_rules = ('-user.tasks', '-project.tasks', '-created_at', '-updated_at',)

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, db.CheckConstraint('len(description) <= 250', name='max_task_description_length'))
    status = db.Column(db.String, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    priority = db.Column(db.Integer, db.CheckConstraint('priority > 0', name='positive_priority'), nullable=False)
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    assigned_to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))

    @validates('title')
    def validate_task_title(self, key, title):
        tasks = Task.query.all()
        task_titles = [task.title for task in tasks]
        if not title:
            raise ValueError("Task must have a Title")
        elif title in task_titles:
            raise ValueError("Task Title must be unique")
        return title

    @validates('description')
    def validate_task_description_length(self, key, description):
        if not description:
            raise ValueError("Task must have a Description")
        if len(description) >= 250:
            raise ValueError("Task Description must be less than or equal to 250 characters long.")
        return description
    
    @validates('status')
    def validate_task_status(self, key, status):
        if not status:
            raise ValueError("Task must have a Status")
        return status
    
    @validates('due_date')
    def validate_task_due_date(self, key, due_date):
        if not due_date:
            raise ValueError("Task must have a Due Date")
        return due_date

    @validates('priority')
    def validate_task_priority(self, key, priority):
        if not priority:
            raise ValueError("Task must have an priority.")
        elif int(priority) < 1:
            raise ValueError("Task Priority must be above 0.")
        return priority
        
    @validates('assigned_to_user_id')
    def validate_assigned_to_user_id(self, key, assigned_to_user_id):
        users = User.query.all()
        ids = [user.id for user in users]
        if not assigned_to_user_id:
            raise ValueError("Task must have an Assigned User")
        elif int(assigned_to_user_id) not in ids:
            raise ValueError('Task Assigned User must exist.')
        return assigned_to_user_id
    
    @validates('project_id')
    def validate_project_id(self, key, project_id):
        projects = Project.query.all()
        ids = [project.id for project in projects]
        if not project_id:
            raise ValueError("Task must have a Project Id")
        elif int(project_id) not in ids:
            raise ValueError('Task Project must exist.')
        return project_id

    def __repr__(self):
        return f'<Task #{self.id}, Task Title: {self.title}, Task Status: {self.status}, Task Assigned to: {self.assigned_to_user_id.username}, Task Project: {self.project.title}, Task Priority: {self.priority}, Task Due Date: {self.due_date}>'


class File(db.Model, SerializerMixin):
    __tablename__ = 'files'

    serialize_rules = ('-user.files', '-project.files', '-updated_at',)

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String, nullable=False)
    description = db.Column(db.String, db.CheckConstraint('len(description) <= 250', name='max_file_description_length'))
    file_type = db.Column(db.String, nullable=False)
    size = db.Column(db.Integer, db.CheckConstraint('size > 0', name='positive_size'), nullable=False)
    
    date_uploaded = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    uploaded_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))

    @validates('filename')
    def validate_file_filename(self, key, filename):
        files = File.query.all()
        file_filenames = [file.filename for file in files]
        if not filename:
            raise ValueError("File must have a Filename")
        elif filename in file_filenames:
            raise ValueError("File Filename must be unique")
        return filename

    @validates('description')
    def validate_file_description_length(self, key, description):
        if not description:
            raise ValueError("File must have a Description")
        if len(description) >= 250:
            raise ValueError("File Description must be less than or equal to 250 characters long.")
        return description
    
    @validates('file_type')
    def validate_file_type(self, key, file_type):
        if not file_type:
            raise ValueError("File must have a File Type")
        return file_type

    @validates('size')
    def validate_file_size(self, key, size):
        if not size:
            raise ValueError("File must have a File Size.")
        elif int(size) <= 1:
            raise ValueError("File Size cannot be 0.")
        return size
        
    @validates('uploaded_by_user_id')
    def validate_file_uploaded_by_user_id(self, key, uploaded_by_user_id):
        users = User.query.all()
        ids = [user.id for user in users]
        if not uploaded_by_user_id:
            raise ValueError("File must have an Uploaded by User")
        elif int(uploaded_by_user_id) not in ids:
            raise ValueError('File Uploading User must exist.')
        return uploaded_by_user_id
    
    @validates('project_id')
    def validate_project_id(self, key, project_id):
        projects = Project.query.all()
        ids = [project.id for project in projects]
        if not project_id:
            raise ValueError("File must have a Project Id")
        elif int(project_id) not in ids:
            raise ValueError('File Project must exist.')
        return project_id

    def __repr__(self):
        return f'<File #{self.id}, File Name: {self.filename}, File Type: {self.file_type}, File Size: {self.size}, File Uploaded By: {self.uploaded_by_user_id.username}, File Project: {self.project.title}, File Date Uploaded: {self.date_uploaded}>'

class Team(db.Model, SerializerMixin):
    __tablename__ = 'teams'

    serialize_rules = ('-user.teams', '-project.teams', '-updated_at',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, db.CheckConstraint('len(description) <= 250', name='max_team_description_length'))
 
    date_created = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now()) 

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    projects = db.relationship('Project', backref='team', cascade="all, delete, delete-orphan")

    @validates('name')
    def validate_team_name(self, key, name):
        teams = Team.query.all()
        team_names = [team.name for team in teams]
        if not name:
            raise ValueError("Team must have a Name")
        elif name in team_names:
            raise ValueError("Team Name must be unique")
        return name

    @validates('description')
    def validate_description_length(self, key, description):
        if not description:
            raise ValueError("Team must have a Description")
        if len(description) >= 250:
            raise ValueError("Team Description must be less than or equal to 250 characters long.")
        return description
    
    @validates('created_by_user_id')
    def validate_created_by_user_id(self, key, created_by_user_id):
        users = User.query.all()
        ids = [user.id for user in users]
        if not created_by_user_id:
            raise ValueError("Team must have a User")
        elif int(created_by_user_id) not in ids:
            raise ValueError('Team User must exist.')
        return created_by_user_id

    def __repr__(self):
        return f'<Team #{self.id}, Team Name: {self.name}, Team Created By: {self.created_by_user_id.username}, Team Description: {self.description}, Team Date Created: {self.created_at}>'

class Calendar(db.Model, SerializerMixin):
    __tablename__ = 'calendars'

    serialize_rules = ('-user.calendars', 'created_at', '-updated_at',)

    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String, nullable=False)
    event_description = db.Column(db.String, db.CheckConstraint('len(event_description) <= 250', name='max_event_description_length'))
    event_date = db.Column(db.DateTime, nullable=False)
     
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now()) 

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @validates('event_name')
    def validate_event_name(self, key, event_name):
        calendars = Calendar.query.all()
        event_names = [calendar.event_name for calendar in calendars]
        if not event_name:
            raise ValueError("Calendar must have an Event Name")
        elif event_name in event_names:
            raise ValueError("Calendar Event Name must be unique")
        return event_name

    @validates('event_description')
    def validate_event_description_length(self, key, event_description):
        if not event_description:
            raise ValueError("Calendar must have an Event Description")
        if len(event_description) >= 250:
            raise ValueError("Calendar Event Description must be less than or equal to 250 characters long.")
        return event_description

    @validates('event_date')
    def validate_event_date(self, key, event_date):
        if not event_date:
            raise ValueError("Calendar must have an Event Date")
        return event_date
    
    @validates('created_by_user_id')
    def validate_event_created_by_user_id(self, key, created_by_user_id):
        users = User.query.all()
        ids = [user.id for user in users]
        if not created_by_user_id:
            raise ValueError("Calendar must have a User")
        elif int(created_by_user_id) not in ids:
            raise ValueError('Calendar User must exist.')
        return created_by_user_id

    def __repr__(self):
        return f'<Calendar #{self.id}, Event Name: {self.event_name}, Event Description: {self.event_description}, Event Date: {self.event_date}, Created By: {self.created_by_user_id.username}>'

class Chat_Message(db.Model, SerializerMixin):
    __tablename__ = 'chat_messages'

    serialize_rules = ('-user.chat_messages', '-updated_at',)

    id = db.Column(db.Integer, primary_key=True)
    message_text = db.Column(db.String, db.CheckConstraint('len(message_text) <= 250', name='max_chat_message_length'))
     
    message_date = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now()) 

    sender_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sender = db.relationship('User', foreign_keys=[sender_user_id], back_populates='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_user_id], back_populates='received_messages')


    
    @validates('message_text')
    def validate_event_description_length(self, key, message_text):
        if not message_text:
            raise ValueError("Chat Message must have Message Text")
        if len(message_text) >= 250:
            raise ValueError("Chat Message Message Text must be less than or equal to 250 characters long.")
        return message_text

    @validates('sender_user_id')
    def validate_sender_user_id(self, key, sender_user_id):
        users = User.query.all()
        ids = [user.id for user in users]
        if not sender_user_id:
            raise ValueError("Chat Message must have a Sending User")
        elif int(sender_user_id) not in ids:
            raise ValueError('Chat Message Sending User must exist.')
        return sender_user_id
    
    @validates('receiver_user_id')
    def validate_receiver_user_id(self, key, receiver_user_id):
        users = User.query.all()
        ids = [user.id for user in users]
        if not receiver_user_id:
            raise ValueError("Chat Message must have a Receiving User")
        elif int(receiver_user_id) not in ids:
            raise ValueError('Chat Message Receiving User must exist.')
        return receiver_user_id

    def __repr__(self):
        return f'<Chat_Message #{self.id}, Message Text: {self.message_text}, Message Date: {self.message_date}, Sender: {self.sender_user_id.username}, Receiver: {self.receiver_user_id.username}>'