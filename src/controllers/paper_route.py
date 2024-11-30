# class PaperModel:
#     def __init__(self, db):
#         """
#         Initialize the model with the MongoDB collection.
#         :param db: The PyMongo database instance
#         """
#         self.collection = db.papers  # Assuming the collection is named 'papers'

#     def create_paper(self, pdf_link, subject_code, year, branch, exam, associated_faculty):
#         """
#         Create a new paper entry.
#         :param pdf_link: Link to the uploaded PDF
#         :param subject_code: Subject code of the paper
#         :param year: Year of the paper
#         :param branch: Branch associated with the paper
#         :param exam: Exam type (e.g., mid-term, end-term, suppl, re-mid)
#         :param associated_faculty: Faculty associated with the paper
#         :return: Inserted document ID as a string
#         """
#         paper_data = {
#             "PDF_Link": pdf_link,
#             "Subject_Code": subject_code,
#             "Year": year,
#             "Branch": branch,
#             "Exam": exam,
#             "Associated_Faculty": associated_faculty
#         }
#         result = self.collection.insert_one(paper_data)
#         return str(result.inserted_id)

#     def find_paper_by_subject_code(self, subject_code):
#         """
#         Find a paper by subject code.
#         :param subject_code: Subject code to search for
#         :return: Document with paper details or None
#         """
#         return self.collection.find_one({"Subject_Code": subject_code})

#     def update_paper(self, subject_code, updates):
#         """
#         Update paper details for a specific subject code.
#         :param subject_code: Subject code to identify the paper
#         :param updates: Dictionary of fields to update
#         :return: True if update succeeded, False otherwise
#         """
#         result = self.collection.update_one({"Subject_Code": subject_code}, {"$set": updates})
#         return result.modified_count > 0

#     def delete_paper(self, subject_code):
#         """
#         Delete a paper by subject code.
#         :param subject_code: Subject code of the paper to delete
#         :return: True if deletion succeeded, False otherwise
#         """
#         result = self.collection.delete_one({"Subject_Code": subject_code})
#         return result.deleted_count > 0

#     def get_all_papers(self):
#         """
#         Get all papers in the collection.
#         :return: List of all documents in the collection
#         """
#         return list(self.collection.find({}, {"_id": 0}))  # Excludes the MongoDB `_id` field


# # Initialize the PaperModel
# paper_model = PaperModel(mongo.db)


# @app.route("/paper", methods=["POST"])
# def create_paper():
#     """
#     API endpoint to create a new paper entry.
#     Expects JSON body with keys: PDF_Link, Subject_Code, Year, Branch, Exam, Associated_Faculty
#     """
#     data = request.json
#     try:
#         paper_id = paper_model.create_paper(
#             pdf_link=data["PDF_Link"],
#             subject_code=data["Subject_Code"],
#             year=data["Year"],
#             branch=data["Branch"],
#             exam=data["Exam"],
#             associated_faculty=data["Associated_Faculty"]
#         )
#         return jsonify({"message": "Paper created successfully", "paper_id": paper_id}), 201
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400


# @app.route("/paper/<subject_code>", methods=["GET"])
# def get_paper(subject_code):
#     """
#     API endpoint to retrieve paper details by subject code.
#     """
#     paper_data = paper_model.find_paper_by_subject_code(subject_code)
#     if paper_data:
#         return jsonify(paper_data), 200
#     return jsonify({"error": "Paper not found"}), 404


# @app.route("/paper/<subject_code>", methods=["PUT"])
# def update_paper(subject_code):
#     """
#     API endpoint to update paper details for a specific subject code.
#     Expects JSON body with the fields to update.
#     """
#     updates = request.json
#     success = paper_model.update_paper(subject_code, updates)
#     if success:
#         return jsonify({"message": "Paper updated successfully"}), 200
#     return jsonify({"error": "Failed to update paper"}), 400


# @app.route("/paper/<subject_code>", methods=["DELETE"])
# def delete_paper(subject_code):
#     """
#     API endpoint to delete a paper by subject code.
#     """
#     success = paper_model.delete_paper(subject_code)
#     if success:
#         return jsonify({"message": "Paper deleted successfully"}), 200
#     return jsonify({"error": "Paper not found"}), 404


# @app.route("/paper", methods=["GET"])
# def get_all_papers():
#     """
#     API endpoint to retrieve all papers.
#     """
#     all_papers = paper_model.get_all_papers()
#     return jsonify(all_papers), 200


# if __name__ == "__main__":
#     app.run(debug=True)





#     def create_paper(self, pdf_link, subject_code, year, branch, exam, associated_faculty):
#         """
#         Create a new paper entry.
#         :param pdf_link: Link to the uploaded PDF
#         :param subject_code: Subject code of the paper
#         :param year: Year of the paper
#         :param branch: Branch associated with the paper
#         :param exam: Exam type (e.g., mid-term, end-term, suppl, re-mid)
#         :param associated_faculty: Faculty associated with the paper
#         :return: Inserted document ID as a string
#         """
#         paper_data = {
#             "PDF_Link": pdf_link,
#             "Subject_Code": subject_code,
#             "Year": year,
#             "Branch": branch,
#             "Exam": exam,
#             "Associated_Faculty": associated_faculty
#         }
#         result = self.collection.insert_one(paper_data)
#         return str(result.inserted_id)

#     def find_paper_by_subject_code(self, subject_code):
#         """
#         Find a paper by subject code.
#         :param subject_code: Subject code to search for
#         :return: Document with paper details or None
#         """
#         return self.collection.find_one({"Subject_Code": subject_code})

#     def update_paper(self, subject_code, updates):
#         """
#         Update paper details for a specific subject code.
#         :param subject_code: Subject code to identify the paper
#         :param updates: Dictionary of fields to update
#         :return: True if update succeeded, False otherwise
#         """
#         result = self.collection.update_one({"Subject_Code": subject_code}, {"$set": updates})
#         return result.modified_count > 0

#     def delete_paper(self, subject_code):
#         """
#         Delete a paper by subject code.
#         :param subject_code: Subject code of the paper to delete
#         :return: True if deletion succeeded, False otherwise
#         """
#         result = self.collection.delete_one({"Subject_Code": subject_code})
#         return result.deleted_count > 0

#     def get_all_papers(self):
#         """
#         Get all papers in the collection.
#         :return: List of all documents in the collection
#         """
#         return list(self.collection.find({}, {"_id": 0}))  # Excludes the MongoDB `_id` field


# # Initialize the PaperModel
# paper_model = PaperModel(mongo.db)


# @app.route("/paper", methods=["POST"])
# def create_paper():
#     """
#     API endpoint to create a new paper entry.
#     Expects JSON body with keys: PDF_Link, Subject_Code, Year, Branch, Exam, Associated_Faculty
#     """
#     data = request.json
#     try:
#         paper_id = paper_model.create_paper(
#             pdf_link=data["PDF_Link"],
#             subject_code=data["Subject_Code"],
#             year=data["Year"],
#             branch=data["Branch"],
#             exam=data["Exam"],
#             associated_faculty=data["Associated_Faculty"]
#         )
#         return jsonify({"message": "Paper created successfully", "paper_id": paper_id}), 201
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400


# @app.route("/paper/<subject_code>", methods=["GET"])
# def get_paper(subject_code):
#     """
#     API endpoint to retrieve paper details by subject code.
#     """
#     paper_data = paper_model.find_paper_by_subject_code(subject_code)
#     if paper_data:
#         return jsonify(paper_data), 200
#     return jsonify({"error": "Paper not found"}), 404


# @app.route("/paper/<subject_code>", methods=["PUT"])
# def update_paper(subject_code):
#     """
#     API endpoint to update paper details for a specific subject code.
#     Expects JSON body with the fields to update.
#     """
#     updates = request.json
#     success = paper_model.update_paper(subject_code, updates)
#     if success:
#         return jsonify({"message": "Paper updated successfully"}), 200
#     return jsonify({"error": "Failed to update paper"}), 400


# @app.route("/paper/<subject_code>", methods=["DELETE"])
# def delete_paper(subject_code):
#     """
#     API endpoint to delete a paper by subject code.
#     """
#     success = paper_model.delete_paper(subject_code)
#     if success:
#         return jsonify({"message": "Paper deleted successfully"}), 200
#     return jsonify({"error": "Paper not found"}), 404


# @app.route("/paper", methods=["GET"])
# def get_all_papers():
#     """
#     API endpoint to retrieve all papers.
#     """
#     all_papers = paper_model.get_all_papers()
#     return jsonify(all_papers), 200


# if __name__ == "__main__":
#     app.run(debug=True)
