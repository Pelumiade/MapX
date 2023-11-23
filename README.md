# MapX: Agricultural Data Management

MapX is a comprehensive Django application designed to facilitate the management and optimization of agricultural data. The project empowers field officers and administrators to oversee and enhance farming operations efficiently.

## Introduction

MapX is built to address the complexities of managing agricultural data by providing a scalable and user-friendly solution. It leverages Django's robust framework and Django Rest Framework for creating powerful and secure RESTful APIs.

## Features

- **Entity Modeling:**
  - Define Django models for administrators, field officers, farmers, farmlands, and geographical details.
  - Establish relationships between entities to represent the agricultural system's structure.

- **Data Calculations:**
  - Implement dynamic calculations for tracking the progress level of field officers based on assigned farmers and mapped farmlands.

- **API Endpoints:**
  - Utilize Django Rest Framework to create comprehensive API endpoints.
  - Features include creating and managing field officers, farmers, mapping farmlands, and exporting data to CSV.

- **User Management:**
  - Implement user creation and management, including the automatic sending of login credentials via email upon account creation for field officers.

- **Geo-Location Handling:**
  - Manage geo-location data with a focus on farmland mapping, including coordinates and associated details.

- **Dashboard and Statistics:**
  - Provide a global dashboard API endpoint offering statistics such as field officer counts, mapped/unmapped farmlands, and other relevant metrics.

- **Permission Control:**
  - Implement custom permission classes to control access to various views and endpoints, ensuring secure and role-based interactions with the system.

- **Logging and Activities:**
  - Include an activity log system (ActivityLog) to track significant actions within the application for transparency and accountability.



