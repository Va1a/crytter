# crytter 
## dKYP - DON'T Know Your Peer 

A peer-to-peer cryptocurrency exchange platform that enables direct trading between users without KYC requirements. Built with Flask and modern web technologies.

## Features

- **Peer-to-Peer Trading**: Create and respond to cryptocurrency exchange offers
- **Multi-Currency Support**: Trade between various cryptocurrencies and fiat currencies including:
  - Cryptocurrencies: BTC, ETH, BCH, XRP, XMR, BRD, DOGE, ADA, BNB, LTC
  - Fiat: USD, EUR, GBP, CHF
- **Real-Time Exchange Rates**: Live currency rates powered by Coinbase API
- **Reputation System**: 
  - User rating system with impact weights
  - Visual reputation badges
  - Detailed trading history
- **Security Features**:
  - Password hashing with bcrypt
  - CSRF protection
  - reCAPTCHA integration
  - Session management
- **User Features**:
  - Customizable profiles
  - Trading alerts system
  - Comment system on offers
  - Offer management
  - Search and filtering capabilities

## Technical Stack

- **Backend**: Python/Flask
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: 
  - Bootstrap 4
  - jQuery
  - Custom CSS
  - Font Awesome icons
- **APIs**: Coinbase Exchange Rates API

## Installation

1. Clone the repository
```bash
git clone [repository-url]
cd dkyp
```

2. Set up a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
# Required environment variables
DKYP-SECRET-KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost/dbname
RECAPTCHA-SITE-KEY=your-recaptcha-site-key
RECAPTCHA-SECRET-KEY=your-recaptcha-secret-key
```

5. Initialize the database
```bash
flask db upgrade
```

6. Run the development server
```bash
python run.py
```

The application will be available at `http://localhost:8000`

## Project Structure

```
crytter/
├── __init__.py          # Flask app initialization
├── config.py            # Configuration settings
├── models.py            # Database models
├── errors/             # Error handlers
├── main/               # Main routes and forms
├── posts/             # Post-related functionality
├── users/             # User management
├── static/            # Static files (CSS, JS, images)
└── templates/         # Jinja2 templates
```

## Security Notice

This platform is designed for peer-to-peer trading. Users are responsible for:
- Verifying trading partners
- Securing their own transactions
- Following local regulations
- Maintaining account security

## Contributing

Contributions are welcome!

## License

See LICENSE file.

## Disclaimer

This platform is provided as-is without any guarantees. Users are responsible for their own trading activities and compliance with local regulations.
