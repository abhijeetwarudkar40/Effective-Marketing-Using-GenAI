"""Persistence for the added Finora campaign lifecycle modules."""
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
import json

DB_PATH=Path(__file__).resolve().parent/"data"/"finora_campaigns.db"

def conn():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c

def init_db():
    c=conn()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS campaigns (
      id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id TEXT, segment TEXT,
      product_name TEXT, objective TEXT, subject TEXT, body TEXT, status TEXT,
      compliance_score INTEGER, created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS approvals (
      id INTEGER PRIMARY KEY AUTOINCREMENT, campaign_id INTEGER, action TEXT,
      notes TEXT, created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS deliveries (
      id INTEGER PRIMARY KEY AUTOINCREMENT, campaign_id INTEGER, channel TEXT,
      recipient TEXT, status TEXT, provider_message TEXT, created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS creative_assets (
      id INTEGER PRIMARY KEY AUTOINCREMENT, campaign_id INTEGER, creative_id TEXT,
      option_no INTEGER, path TEXT, sha256 TEXT, approval_status TEXT,
      created_at TEXT
    );
    """); c.commit(); c.close()

def save_campaign(campaign,status="Draft",score=None):
    c=conn()
    cur=c.execute("""INSERT INTO campaigns
    (customer_id,segment,product_name,objective,subject,body,status,compliance_score,created_at)
    VALUES(?,?,?,?,?,?,?,?,?)""",(
      campaign.get("customer_id"),campaign.get("primary_segment",campaign.get("segment")),
      campaign.get("product_name"),campaign.get("campaign_objective"),
      campaign.get("subject",campaign.get("subject_line")),campaign.get("body"),status,score,
      datetime.now(timezone.utc).isoformat()))
    c.commit(); i=cur.lastrowid; c.close(); return i

def update_status(i,status):
    c=conn(); c.execute("UPDATE campaigns SET status=? WHERE id=?",(status,i)); c.commit(); c.close()

def log_approval(i,action,notes=""):
    c=conn(); c.execute("INSERT INTO approvals(campaign_id,action,notes,created_at) VALUES(?,?,?,?)",
                         (i,action,notes,datetime.now(timezone.utc).isoformat())); c.commit(); c.close()

def log_delivery(i,channel,recipient,status,message=""):
    c=conn(); c.execute("""INSERT INTO deliveries
      (campaign_id,channel,recipient,status,provider_message,created_at)
      VALUES(?,?,?,?,?,?)""",(i,channel,recipient,status,message,datetime.now(timezone.utc).isoformat()))
    c.commit(); c.close()

def campaigns():
    c=conn(); rows=c.execute("SELECT * FROM campaigns ORDER BY id DESC").fetchall(); c.close(); return [dict(x) for x in rows]

def deliveries():
    c=conn(); rows=c.execute("SELECT * FROM deliveries ORDER BY id DESC").fetchall(); c.close(); return [dict(x) for x in rows]

init_db()
