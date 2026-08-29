# Python Scripting Examples

Three Python projects covering log analysis, TCP networking, desktop interfaces, and Flask web development.

## Task management analyser example

The command-line program parses members, managers, teams, and tasks from a text log. It can list urgent tasks, compare team workloads, find managers by expertise, and filter tasks by property.

This project demonstrates regular-expression parsing, object-oriented modeling, file processing, command-line arguments, dictionaries, and turning unstructured text into useful reports.

```text
Select report: Urgent Tasks
[B1] API Development - assigned to jdoe
```

## Bookstore client-server example

A TCP server handles authentication, inventory, discounts, transactions, and sales reports. Tkinter clients provide separate cashier and manager interfaces.

This project is an example of client-server architecture. It covers socket communication, message-protocol design, GUI event handling, shared data, transaction processing, and the need for synchronization when multiple clients access the same files.

```text
Client: transaction;2025-11-15 10:30:00;;john;1003-2
Server: transactionconfirmation;19.50
```

## Local event portal example

A Flask and SQLite website where visitors search campus events and registered users publish their own events. Sessions protect user pages, while admin accounts manage societies.

This project demonstrates how the front end, server, and database work together in a web application. It applies routing, form validation, authentication, session management, relational data, role-based access, and server-side HTML rendering.

```text
Visitor -> Search events -> View details
User    -> Login -> Announce event -> Manage profile
Admin   -> Login -> Manage societies
```

## Author

Barış Şan
