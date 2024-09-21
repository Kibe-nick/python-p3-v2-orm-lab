from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        if not isinstance(year, int):
            raise ValueError("Year must be an integer.")
        if year < 2000:
            raise ValueError("Year must be greater than or equal to 2000.")
        if not summary or len(summary.strip()) == 0:
            raise ValueError("Summary cannot be empty.")
        
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        # Validate that employee_id exists in the Employee table
        if not Employee.find_by_id(value):
            raise ValueError("Employee ID must reference a valid employee.")
        self._employee_id = value


    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        if self.id:
        # Update an existing review
            CURSOR.execute('''UPDATE reviews
                              SET year = ?, summary = ?, employee_id = ?
                              WHERE id = ?; ''', 
                            (self.year, self.summary, self.employee_id, self.id))
        else:
        # Insert a new review
            CURSOR.execute('''INSERT INTO reviews (year, summary, employee_id)
                              VALUES (?, ?, ?); ''', 
                            (self.year, self.summary, self.employee_id))
        # Fetch the ID of the new row
        self.id = CURSOR.lastrowid

    # Add the review instance to the dictionary
        Review.all[self.id] = self
        CONN.commit()

                             



    @classmethod
    def create(cls, year, summary, employee_id):
        """Initialize a new Review instance and save the object to the database. Return the new instance."""
        review = cls(year, summary, employee_id)
        # Save the new instance 
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance having the attribute values from the table row."""
        return cls(id=row[0], year=row[1], summary=row[2], employee_id=row[3])
    


    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance having the attribute values from the table row."""
        CURSOR.execute('SELECT * FROM reviews WHERE id = ?;', (id,))
        row = CURSOR.fetchone()
        # If a row is found, return the instance from the database
        if row:
            return cls.instance_from_db(row)
        return None

    def update(self):
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        Review.all[self.id] = self
        CONN.commit()

    def delete(self):
        sql = """
            DELETE FROM reviews WHERE id = ?
        """
        CURSOR.execute(sql, (self.id,))
        Review.all.pop(self.id, None)
        self.id = None
        CONN.commit()

    @classmethod
    def get_all(cls):
        sql = """
            SELECT * FROM reviews
        """
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]
