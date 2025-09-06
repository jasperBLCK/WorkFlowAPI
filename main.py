from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import User, Task
from schemas import TasksUpdate, UserCreate, UserLogin, UserRead, TaskCreate, TaskRead
import hash
from authx import AuthX, AuthXConfig

Base.metadata.create_all(bind=engine)

app = FastAPI()

config = AuthXConfig()
config.JWT_SECRET_KEY = "" 
config.JWT_ACCESS_COOKIE_NAME = "access token" 
config.JWT_TOKEN_LOCATION = ['cookies'] 
security = AuthX(config=config)

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#-------------------------------------------------------------------#

@app.post("/register", response_model=UserRead)
async def user_create(user: UserCreate, db: Session = Depends(get_db)):
    hashed = hash.hash_password(user.password_hash)
    db_user = User(login=user.login, password_hash=hashed, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/login")
async def user_login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.login == user.login).first()
    
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid login or password")
    
    if not hash.verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid login or password")
    
    token = security.create_access_token(uid=str(db_user.id))
    return {"message": "Login successful", "token": token}

#--------------------------------------------------------------------------#


@app.post('/tasks', response_model=TaskRead)
async def create_tasks(task: TaskCreate, db: Session = Depends(get_db)):
    db_tasks = Task(worker=task.worker, title=task.title, description=task.description, status=task.status)    
    db_worker = db.query(User).filter(User.login == task.worker).first()
    if not db_worker:
        raise HTTPException(404, 'Worker not found!')
    
    db.add(db_tasks)
    db.commit()
    db.refresh(db_tasks)
    return db_tasks



@app.get('/tasks/{worker}')
async def worker_task(name: str, db: Session = Depends(get_db)):
    db_check = db.query(Task).filter(Task.worker == name).all()
    if not db_check:
        raise HTTPException(404, 'Worker not found!')
    return db_check



@app.get('/tasks')
async def get_all_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()



@app.delete('/tasks/{id}')
async def task_delete(id: int, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == id).first()
    db.delete(db_task)
    db.commit()
    
    return {'Message': f'Task Number:[#{id}] Deleted!'}



@app.put('/tasks/{edit}', response_model=TasksUpdate)
async def task_edit(task_id: int, new: TasksUpdate, db: Session = Depends(get_db)):
    db_taskID = db.query(Task).filter(Task.id == task_id).first()
    if not db_taskID:
        raise HTTPException(status_code='404', detail=f'ID:{task_id} Not Found')
    if new.title is not None:
        db_taskID.title = new.title
    if new.description is not None:
        db_taskID.description = new.description
    if new.status is not None:
        db_taskID.status = new.status
    
    db.commit()
    db.refresh(db_taskID)
    
    return JSONResponse(content={'Message': f'Task Number:[#{task_id}] Updated!'})
#-----------------------------------------------------------------------#
