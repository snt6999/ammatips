from datetime import datetime, timedelta, timezone
from secrets import compare_digest
import hashlib, hmac, secrets
from jose import jwt, JWTError
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from .config import settings
from .database import Base, engine, get_db, SessionLocal
from .models import Product, Order
from .schemas import LoginRequest, ProductPayload, CreateOrderRequest, StatusUpdate

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
security = HTTPBearer(auto_error=False)
ALGORITHM = "HS256"

def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 240_000)
    return salt.hex() + "$" + derived.hex()

def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, hash_hex = stored.split("$", 1)
        expected = bytes.fromhex(hash_hex)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 240_000)
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False

def token_for_admin():
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode({"sub": settings.admin_email.lower(), "role": "admin", "exp": exp}, settings.jwt_secret, algorithm=ALGORITHM)

def require_admin(credentials: HTTPAuthorizationCredentials | None = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Admin authentication required")
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[ALGORITHM])
        if payload.get("role") != "admin" or payload.get("sub") != settings.admin_email.lower():
            raise HTTPException(status_code=403, detail="Admin access required")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired admin token")
    return payload

def product_dict(p: Product):
    return {"id":p.id,"title":p.title,"subtitle":p.subtitle,"category":p.category,"price":p.price,
            "oldPrice":p.oldPrice,"emoji":p.emoji,"color":p.color,"description":p.description,
            "features":p.features or [],"featured":p.featured,"active":p.active}

def order_dict(o: Order):
    return {"id":o.id,"order_number":o.order_number,"customer_name":o.customer_name,"phone":o.phone,
            "email":o.email,"transaction_id":o.transaction_id,"note":o.note,"items":o.items or [],
            "amount":o.amount,"status":o.status,
            "created_at":o.created_at.isoformat() if o.created_at else None,
            "updated_at":o.updated_at.isoformat() if o.updated_at else None}

SEED_PRODUCTS = [
 {"id":"p1","title":"Tantrum Time Telugu Guide","subtitle":"ఏడుపు, కోపం వచ్చినప్పుడు ఏం చెప్పాలి?","category":"Emotions","price":149,"oldPrice":249,"emoji":"🌈","color":"peach","description":"Tantrum సమయంలో parent calmగా ఉండటానికి, childతో connect అవ్వడానికి practical Telugu scripts, do/don’t examples, and after-tantrum steps.","features":["Exact Telugu sentences","What to say / what not to say","Before-during-after checklist","Printable quick reference"],"featured":True},
 {"id":"p2","title":"Happy Morning Routine Kit","subtitle":"Morning rush తగ్గించే simple system","category":"Routines","price":99,"oldPrice":149,"emoji":"☀️","color":"yellow","description":"Getting-ready struggles తగ్గించడానికి picture routine, parent checklist, and child-friendly choices.","features":["Morning routine chart","Night-before checklist","2-minute transition ideas","Printable A4 sheets"],"featured":True},
 {"id":"p3","title":"Food Time Without Fights","subtitle":"Food strugglesకి pressure-free practical guide","category":"Food","price":129,"oldPrice":199,"emoji":"🍓","color":"mint","description":"Mealtime pressure తగ్గించి predictable routine create చేయడానికి family-friendly practical ideas.","features":["Mealtime routine","Neutral phrases to try","Parent do/don’t guide","When to seek professional advice"],"featured":True},
 {"id":"p4","title":"Screen Time Family Plan","subtitle":"Screen boundaries కోసం clear family system","category":"Screen time","price":129,"oldPrice":199,"emoji":"📵","color":"lavender","description":"Screen transitions, clear boundaries, alternatives, and consistent parent responses కోసం practical plan.","features":["Family screen rules worksheet","Transition scripts","Alternative activity list","Weekly tracker"],"featured":False},
 {"id":"p5","title":"Bedtime Made Easier","subtitle":"Bedtime routine & calming scripts","category":"Sleep","price":99,"oldPrice":149,"emoji":"🌙","color":"blue","description":"Bedtimeకు ముందే predictable routine, connection time, and gentle limits plan చేసుకోవడానికి guide.","features":["Bedtime visual chart","Wind-down routine","Common objections scripts","Printable tracker"],"featured":False},
 {"id":"p6","title":"Little Independence Pack","subtitle":"2–6 years kidsకి చిన్న పనులు నేర్పించండి","category":"Independence","price":179,"oldPrice":249,"emoji":"🧩","color":"pink","description":"Age-appropriate everyday independence skillsను చిన్న stepsగా నేర్పించడానికి parent-friendly printable pack.","features":["Skill-building checklist","Choice scripts","Practice tracker","Praise without pressure"],"featured":False}
]

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.scalar(select(Product.id).limit(1))
        if not existing:
            for data in SEED_PRODUCTS:
                db.add(Product(**data))
            db.commit()
    finally:
        db.close()

@app.get("/")
def root():
    return {"name":settings.app_name,"status":"ok","docs":"/docs"}

@app.get("/health")
def health():
    return {"status":"healthy"}

@app.post("/api/auth/login")
def login(body: LoginRequest):
    if not compare_digest(body.email.strip().lower(), settings.admin_email.strip().lower()) or not verify_password(body.password, hash_password(settings.admin_password, bytes.fromhex("00112233445566778899aabbccddeeff"))):
        # Fixed-salt hash comparison avoids storing the plaintext admin password in the app.
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return {"access_token":token_for_admin(),"token_type":"bearer","admin_email":settings.admin_email}

@app.get("/api/products")
def list_products(db: Session = Depends(get_db)):
    products = db.scalars(select(Product).where(Product.active == True).order_by(Product.title)).all()
    return [product_dict(p) for p in products]

@app.post("/api/orders")
def create_order(body: CreateOrderRequest, db: Session = Depends(get_db)):
    # Payment remains pending until an administrator verifies the transaction independently.
    seen = db.scalar(select(Order.id).where(Order.transaction_id == body.transaction_id.strip()))
    if seen:
        raise HTTPException(status_code=409, detail="This transaction reference has already been submitted")
    line_items, amount = [], 0.0
    for item in body.items:
        product = db.get(Product, item.product_id)
        if not product or not product.active:
            raise HTTPException(status_code=400, detail=f"Product unavailable: {item.product_id}")
        line_total = round(product.price * item.quantity, 2)
        amount += line_total
        line_items.append({"product_id":product.id,"title":product.title,"price":product.price,"quantity":item.quantity,"line_total":line_total})
    order_number = "TAT-" + secrets.token_hex(4).upper()
    order = Order(order_number=order_number,customer_name=body.customer_name.strip(),phone=body.phone.strip(),
                  email=(body.email or "").strip() or None,transaction_id=body.transaction_id.strip(),
                  note=body.note.strip(),items=line_items,amount=round(amount,2),status="pending")
    db.add(order)
    db.commit()
    db.refresh(order)
    return order_dict(order)

@app.post("/api/admin/products", dependencies=[Depends(require_admin)])
def create_product(body: ProductPayload, db: Session = Depends(get_db)):
    data = body.model_dump(by_alias=False)
    product_id = body.id or "p-" + secrets.token_hex(6)
    if db.get(Product, product_id):
        raise HTTPException(status_code=409, detail="Product ID already exists")
    p = Product(id=product_id,title=data["title"],subtitle=data["subtitle"],category=data["category"],price=data["price"],
                oldPrice=data["old_price"],emoji=data["emoji"],color=data["color"],description=data["description"],
                features=data["features"],featured=data["featured"],active=data["active"])
    db.add(p); db.commit(); db.refresh(p)
    return product_dict(p)

@app.put("/api/admin/products/{product_id}", dependencies=[Depends(require_admin)])
def update_product(product_id: str, body: ProductPayload, db: Session = Depends(get_db)):
    p = db.get(Product, product_id)
    if not p: raise HTTPException(status_code=404, detail="Product not found")
    data = body.model_dump(by_alias=False)
    for field, value in {"title":data["title"],"subtitle":data["subtitle"],"category":data["category"],"price":data["price"],
                         "oldPrice":data["old_price"],"emoji":data["emoji"],"color":data["color"],"description":data["description"],
                         "features":data["features"],"featured":data["featured"],"active":data["active"]}.items():
        setattr(p, field, value)
    db.commit(); db.refresh(p)
    return product_dict(p)

@app.delete("/api/admin/products/{product_id}", dependencies=[Depends(require_admin)])
def delete_product(product_id: str, db: Session = Depends(get_db)):
    p = db.get(Product, product_id)
    if not p: raise HTTPException(status_code=404, detail="Product not found")
    p.active = False
    db.commit()
    return {"ok":True,"message":"Product deactivated"}

@app.get("/api/admin/orders", dependencies=[Depends(require_admin)])
def list_orders(db: Session = Depends(get_db)):
    orders = db.scalars(select(Order).order_by(desc(Order.created_at))).all()
    return [order_dict(o) for o in orders]

@app.patch("/api/admin/orders/{order_id}/status", dependencies=[Depends(require_admin)])
def set_order_status(order_id: int, body: StatusUpdate, db: Session = Depends(get_db)):
    if body.status not in ("approved","rejected"):
        raise HTTPException(status_code=400, detail="Status must be approved or rejected")
    order = db.get(Order, order_id)
    if not order: raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "pending":
        raise HTTPException(status_code=409, detail="Only pending orders can be reviewed")
    order.status = body.status
    order.updated_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(order)
    return order_dict(order)
