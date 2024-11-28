class PaperModel:
    def __init__(self, db):
        """
        Initialize the model with the MongoDB collection.
        :param db: The PyMongo database instance
        """
        self.collection = db.papers  # Assuming the collection is named 'papers'

    def create_paper(self, pdf_link, subject_code, year, branch, exam, associated_faculty):
        """
        Create a new paper entry.
        :param pdf_link: Link to the uploaded PDF
        :param subject_code: Subject code of the paper
        :param year: Year of the paper
        :param branch: Branch associated with the paper
        :param exam: Exam type (e.g., mid-term, end-term, suppl, re-mid)
        :param associated_faculty: Faculty associated with the paper
        :return: Inserted document ID as a string
        """
        paper_data = {
            "PDF_Link": pdf_link,
            "Subject_Code": subject_code,
            "Year": year,
            "Branch": branch,
            "Exam": exam,
            "Associated_Faculty": associated_faculty
        }
        result = self.collection.insert_one(paper_data)
        return str(result.inserted_id)

    def find_paper_by_subject_code(self, subject_code):
        """
        Find a paper by subject code.
        :param subject_code: Subject code to search for
        :return: Document with paper details or None
        """
        return self.collection.find_one({"Subject_Code": subject_code})

    def update_paper(self, subject_code, updates):
        """
        Update paper details for a specific subject code.
        :param subject_code: Subject code to identify the paper
        :param updates: Dictionary of fields to update
        :return: True if update succeeded, False otherwise
        """
        result = self.collection.update_one({"Subject_Code": subject_code}, {"$set": updates})
        return result.modified_count > 0

    def delete_paper(self, subject_code):
        """
        Delete a paper by subject code.
        :param subject_code: Subject code of the paper to delete
        :return: True if deletion succeeded, False otherwise
        """
        result = self.collection.delete_one({"Subject_Code": subject_code})
        return result.deleted_count > 0

    def get_all_papers(self):
        """
        Get all papers in the collection.
        :return: List of all documents in the collection
        """
        return list(self.collection.find({}, {"_id": 0}))  # Excludes the MongoDB `_id` field
