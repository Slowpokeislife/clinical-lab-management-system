# Clinical Laboratory Management — Public Demo

Offline-first desktop application for small laboratory operations, built with Python, Tkinter, SQLite and Excel interoperability.

**This is a reimplemented, anonymized portfolio demonstration**, not the original company's software. It contains no production databases, identities, contact details, credentials or company branding. All samples are synthetic; it is not for production or clinical decision-making.

## Architecture

`Tkinter interface -> Python business logic -> SQLite local_data/demo.sqlite3 -> openpyxl Excel exports`

Key capabilities:
- Customer CRUD (create, view, edit)
- Study catalog with pricing and direct cost management
- Multi-item sale capture, unique folios and partial payments
- Branch-specific operational Excel receipts and financial summaries
- Import/export of customers and study catalogs to Excel
- Local PBKDF2 password verification; no network services or email

## Run on Windows

Use Python 3.11+.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/init_demo.py --password "Choose-Your-Own-Demo-Password-123"
python main.py
```

Login username: `demo`. Password: the value supplied to `init_demo.py`.

The application runs without Internet after dependencies are installed. The SQLite database and all generated Excel files are intentionally excluded from Git.

## Financial definitions

- **Sales/revenue**: sum of quantity × price, recorded at sale time.
- **Direct cost**: sum of quantity × direct cost captured at sale time.
- **Gross margin**: sales minus direct cost. Not net profit.
- **Payment**: amount received at sale time.
- **Outstanding balance**: sale total minus payment.

## Security and scope

- All example names and emails are fictional placeholders.
- No SMTP integration, API keys, company identity, real medical records or tax identifiers.
- The import feature is meant for invented demo data only; do not import real records into a public portfolio demonstration.
- Authentication is local and illustrative; do not deploy this as a production medical system.
- Public demo source is not a representation of the entire original production system.

## Portfolio framing

**Business Process Automation · Data Management · Offline-first Architecture · Excel Reporting**
