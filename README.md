# Telugu Amma Tips — Parenting Digital Store

A mobile-first Telugu parenting brand website with a digital product storefront, WhatsApp support, manual UPI/PhonePe QR payment submission, and admin order approval.

## Project structure
- `frontend/` React + Vite website, ready for Netlify
- `backend/` FastAPI API, ready for Render
- `netlify.toml` Netlify SPA configuration

## Important payment/security note
This starter supports **manual payment verification**: the customer pays using your configured UPI QR, submits a transaction reference, and an admin reviews it. It does not automatically verify payments with PhonePe. Never mark an order paid solely because a customer uploaded a screenshot; verify the transaction in your own merchant/bank app.

The frontend includes a local demo mode when `VITE_API_URL` is not configured. Local demo data is stored in that browser only and is not shared between customers. For real customer orders and admin approvals, deploy the backend to Render and configure the frontend to use it. Do not use demo mode for production sales.

## 1. Frontend local run
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
Open the URL printed by Vite.

## 2. Configure frontend
Edit `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
VITE_WHATSAPP_NUMBER=919876543210
VITE_UPI_ID=yourname@upi
VITE_UPI_NAME=Telugu Amma Tips
VITE_PHONEPE_QR_IMAGE_URL=
```
- WhatsApp number: international digits only, no `+` or spaces.
- UPI ID: your real merchant/personal UPI ID.
- QR image URL: optional public HTTPS URL to your PhonePe/UPI QR image. You can also add a QR image file to `frontend/public/phonepe-qr.png` and set `VITE_PHONEPE_QR_IMAGE_URL=/phonepe-qr.png`.
- Do not put secret API keys in frontend environment variables.

## 3. Backend local run
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload
```
API docs: http://localhost:8000/docs

Default local admin account is created from environment variables. Change it before deployment:
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`
- `JWT_SECRET`

## 4. Supabase PostgreSQL setup (production database)
1. Create a project at [Supabase](https://supabase.com/).
2. In Supabase, open **Project Settings → Database → Connection string**.
3. Choose the **Session pooler** connection string if Render cannot reach the direct database host over IPv6. Copy the URI format shown by Supabase and replace its password placeholder with your database password. The app accepts `postgres://`, `postgresql://`, and `postgresql+psycopg://` URLs and adds `sslmode=require` when it is missing.
4. Keep the connection string private. Never put it in a `VITE_` frontend variable or commit it to Git.
5. On first successful backend startup, SQLAlchemy creates the `products` and `orders` tables and inserts the starter products if the products table is empty. No manual SQL script is required for this starter.

## 5. Render backend deployment
- Create a new **Web Service** from the `backend` directory (or set Root Directory to `backend`).
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Add environment variables from `backend/.env.example` in the Render dashboard.
- Set `DATABASE_URL` to the private Supabase PostgreSQL connection string from the previous section.
- Set `CORS_ORIGINS` to your exact Netlify site URL, comma-separated if you use a custom domain too.
- Replace `JWT_SECRET` with a long random secret and change `ADMIN_EMAIL` / `ADMIN_PASSWORD` before public launch.
- After deploy, visit `https://YOUR-API.onrender.com/health` and `https://YOUR-API.onrender.com/docs` to check the service.

The default `sqlite:///./telugu_amma_tips.db` remains useful for local development only. For a live store, use Supabase PostgreSQL so orders and admin changes persist across backend restarts.

## 6. Netlify frontend deployment
- Connect the repository or upload the frontend project to Netlify.
- Build command: `npm run build`
- Publish directory: `dist`
- Set environment variables in Netlify:
  - `VITE_API_URL` = your Render backend URL, e.g. `https://your-api.onrender.com`
  - `VITE_WHATSAPP_NUMBER`
  - `VITE_UPI_ID`
  - `VITE_UPI_NAME`
  - `VITE_PHONEPE_QR_IMAGE_URL` (optional)
- Redeploy after changing environment variables.

## Admin
Visit `/admin`. Sign in with the backend admin email/password. In local demo mode, use `admin@teluguammatips.in` / `ChangeMe123!` (demo only). For API mode, use the credentials configured on Render. Change demo credentials before public launch.

## Included features
- Responsive homepage and product cards
- Search/filter products
- Product details and cart
- UPI/PhonePe QR payment instructions
- Submit transaction reference and order
- WhatsApp contact button and product enquiry links
- Admin login, dashboard summary, product CRUD, pending-payment approval/rejection
- API-backed product/order management
- Local demo mode for preview without backend

## Before launch checklist
- Replace placeholder products, prices, WhatsApp number, UPI ID and QR image.
- Use HTTPS for both sites.
- Deploy the backend and configure CORS.
- Confirm Render `DATABASE_URL` points to your Supabase PostgreSQL project, not SQLite.
- Change admin credentials and JWT secret.
- Publish your refund, privacy, terms, delivery and support policies.
- Test an end-to-end low-value order and verify payment manually before approving.

## Database notes
- Tables are managed by SQLAlchemy at backend startup: `products` and `orders`.
- Admin credentials are environment variables, not database user accounts. Keep the admin password and `JWT_SECRET` private.
- This starter does not store customer passwords or implement customer registration; checkout collects order contact details only.
- The app uses manual PhonePe/UPI verification. Supabase stores order status, but does not verify a PhonePe transaction automatically.
