# Learning Notes

Here is a section of what I learned from this project:

## Docker builds
During the development of this Flask API, I compared the build process between **single-stage** and **multi-stage** Dockerfiles. Here are some of the findings:
- Single-stage build: 
  - Time taken: Approximately 0.50s
  - Process:
    - All dependencies, including build tools and caches, are installed into the same image.
    - The final image size is larger due to the inclusion of build tools and extra files.
- Multi-Stage Build
  - Time Taken: Approximately 0.32s
  - Process:
    - Dependencies are installed in a separate builder stage, and only the necessary files (like the app and required libraries) are copied into the final image.
    - The final image is smaller and cleaner, containing only the essential runtime environment.
- Conclusion:
  - Multi-Stage Builds are faster and create smaller, cleaner images than single-stage builds.
  - For small apps like this one, the difference in build time might not be significant, but the resulting image size is smaller and more efficient.
  - Multi-stage builds are particularly useful when you want to separate build dependencies from production runtime, reducing security risks and keeping images optimized.

## Archiving Data

While building the database schema for this project, I also learned how real-world apps handle archiving old or inactive data.

- Why archive data?
  - To keep the main tables small and fast.
  - To separate active records from old/inactive ones.
  - To follow data retention rules (e.g., keep inactive student records for one year).
- How archiving usually works:
  - Add an `is_archived` column to tables like students, instructors, or courses.
  - Use the `updated_at` column to track when each record was last changed.
  - Combine `updated_at` with a status field (like the `status` column in the students table) to decide whether a record is inactive.
  - If a student has an inactive status and hasn’t been updated for a long time (e.g., one year), the record can be marked as archived or moved to an archive table.
- What I learned:
  - Archiving based on `updated_at` along with the record’s status is a more accurate approach.
  - It helps reduce clutter and keeps recent data easy to access.
  - Users like students aren’t archived immediately — they are given time before being flagged.
- Sources I referenced:
  - [Data archiving best practice](https://success.outsystems.com/documentation/outsystems_developer_cloud/building_apps/data_management/best_practices_for_data_management/data_archiving_best_practice)
  - [Efficient Data Management: Overcoming the Challenges of Large Tables with an Archival Strategy](https://opensource-db.com/efficient-data-management-overcoming-the-challenges-of-large-tables-with-an-archival-strategy)
  
## Database Connection

While building the database layer for this project, I explored how to manage SQLite connections in a clean and safe way.

- Why close the database connection after each operation?
  - Prevents database locks and memory issues, especially in SQLite.
  - Ensures connections aren’t left open accidentally.
  - Each API call is independent, so there’s no need to keep the connection open.
- How I applied it:
  - Updated the Database class to call self.close() in a finally block after every execute_query, execute_many, and execute_script call.
  - This guarantees the connection is closed, even if an error happens during execution.
- What I learned:
  - For SQLite, it’s generally better to open and close the connection for each operation to avoid issues and keep things simple.
  - In larger SQL databases (like PostgreSQL or MySQL), keeping a persistent connection (e.g., using connection pooling) is more common for performance.
    - sources:
      - [PostgreSQL Connection Pooling](https://www.compilenrun.com/docs/database/postgresql/postgresql-best-practices/postgresql-connection-pooling/?utm_source=chatgpt.com)
      - [Why Connection Pooling Is Essential for PostgreSQL Database Optimisation](https://caw.tech/why-connection-pooling-is-essential-for-postgresql-database-optimisation/)
  - Since this is a small app using SQLite, closing the connection after each use is a good, safe choice.