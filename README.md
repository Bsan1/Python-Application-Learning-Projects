# Python Application Learning Projects

Three technical projects developed to practice text processing, network programming, desktop interfaces, and database-backed web development with Python.

## Task log analyzer

A command-line application that parses members, managers, teams, and tasks from a structured text log. It can list urgent tasks, compare team workloads, find managers by expertise, and filter tasks by selected properties.

The project focuses on regular-expression parsing, object-oriented modeling, file processing, command-line arguments, dictionaries, and converting raw text into useful reports.

```text
Select report: Urgent Tasks
[B1] API Development - assigned to jdoe
```

Contributor: Barış Şan

## TCP bookstore application

A TCP server manages authentication, inventory, discount codes, transactions, and sales reports. Separate Tkinter clients provide cashier and manager interfaces.

The project explores client-server architecture, socket communication, message-protocol design, GUI event handling, transaction processing, and synchronization when multiple clients access shared files.

```text
Client: transaction;2025-11-15 10:30:00;;john;1003-2
Server: transactionconfirmation;19.50
```

Contributors: Barış Şan and Emmanuel Monye

## Flask event portal

A Flask and SQLite web application where visitors can search events and registered users can publish their own. Sessions protect user pages, while administrator accounts manage societies.

The project brings together routing, form validation, authentication, session management, relational data, role-based access, and server-side HTML rendering.

```text
Visitor -> Search events -> View details
User    -> Sign in -> Publish event -> Manage profile
Admin   -> Sign in -> Manage societies
```

Contributors: Barış Şan and Emmanuel Monye
