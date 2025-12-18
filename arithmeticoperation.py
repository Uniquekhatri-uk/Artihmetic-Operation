import re
import tkinter as tk
from tkinter import messagebox
from rdflib import Graph, Namespace, RDF
import os

# ----------------------------
# Built-in Arithmetic Ontology (Turtle)
# ----------------------------
ARITH_TTL = r"""
@prefix : <http://example.org/arithmetic-its#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@base <http://example.org/arithmetic-its#> .

<http://example.org/arithmetic-its#ArithmeticITS> rdf:type owl:Ontology .

:hasCommonError rdf:type owl:ObjectProperty ; rdfs:domain :Operation ; rdfs:range :ErrorType .
:hasRule rdf:type owl:ObjectProperty ; rdfs:domain :Operation ; rdfs:range :ArithmeticRule .

:errorHint rdf:type owl:DatatypeProperty ; rdfs:domain :ErrorType ; rdfs:range xsd:string .
:errorName rdf:type owl:DatatypeProperty ; rdfs:domain :ErrorType ; rdfs:range xsd:string .

:exampleProblem rdf:type owl:DatatypeProperty ; rdfs:domain :ArithmeticRule ; rdfs:range xsd:string .
:exampleSteps rdf:type owl:DatatypeProperty ; rdfs:domain :ArithmeticRule ; rdfs:range xsd:string .
:ruleName rdf:type owl:DatatypeProperty ; rdfs:domain :ArithmeticRule ; rdfs:range xsd:string .
:ruleText rdf:type owl:DatatypeProperty ; rdfs:domain :ArithmeticRule ; rdfs:range xsd:string .

:Addition rdf:type owl:Class ; rdfs:subClassOf :Operation .
:Division rdf:type owl:Class ; rdfs:subClassOf :Operation .
:Multiplication rdf:type owl:Class ; rdfs:subClassOf :Operation .
:Subtraction rdf:type owl:Class ; rdfs:subClassOf :Operation .
:ArithmeticRule rdf:type owl:Class .
:ErrorType rdf:type owl:Class .
:Operation rdf:type owl:Class .

:Add rdf:type owl:NamedIndividual , :Addition ;
  :hasCommonError :err_wrong_operation ;
  :hasRule :rule_addition .

:Divide rdf:type owl:NamedIndividual , :Division ;
  :hasCommonError :err_divide_by_zero , :err_wrong_operation ;
  :hasRule :rule_division .

:Multiply rdf:type owl:NamedIndividual , :Multiplication ;
  :hasCommonError :err_wrong_operation ;
  :hasRule :rule_multiplication .

:Subtract rdf:type owl:NamedIndividual , :Subtraction ;
  :hasCommonError :err_wrong_operation ;
  :hasRule :rule_subtraction .

:err_divide_by_zero rdf:type owl:NamedIndividual , :ErrorType ;
  :errorHint "Division by zero is undefined. The divisor must be non-zero." ;
  :errorName "DivideByZero" .

:err_wrong_operation rdf:type owl:NamedIndividual , :ErrorType ;
  :errorHint "Use keywords: total/altogether → add; remain/left → subtract; each/equal groups → multiply or divide; shared equally → divide." ;
  :errorName "WrongOperation" .

:rule_addition rdf:type owl:NamedIndividual , :ArithmeticRule ;
  :exampleProblem "What is 7 + 5?" ;
  :exampleSteps "Step 1: Identify 7 and 5. Step 2: Add: 7 + 5 = 12." ;
  :ruleName "Addition rule" ;
  :ruleText "Addition combines two or more quantities to make a total." .

:rule_division rdf:type owl:NamedIndividual , :ArithmeticRule ;
  :exampleProblem "12 sweets shared equally among 4 children. Each gets?" ;
  :exampleSteps "Step 1: Total 12. Step 2: 12 ÷ 4 = 3." ;
  :ruleName "Division rule" ;
  :ruleText "Division splits a total into equal parts." .

:rule_multiplication rdf:type owl:NamedIndividual , :ArithmeticRule ;
  :exampleProblem "6 boxes have 4 items each. How many items total?" ;
  :exampleSteps "Step 1: 6 groups of 4. Step 2: 6 × 4 = 24." ;
  :ruleName "Multiplication rule" ;
  :ruleText "Multiplication is repeated addition for equal groups." .

:rule_subtraction rdf:type owl:NamedIndividual , :ArithmeticRule ;
  :exampleProblem "Ali has 10 apples and gives away 3. How many remain?" ;
  :exampleSteps "Step 1: Start with 10. Step 2: Take away 3: 10 - 3 = 7." ;
  :ruleName "Subtraction rule" ;
  :ruleText "Subtraction finds how much remains after taking away." .
"""

EX = Namespace("http://example.org/arithmetic-its#")

OP_FROM_SYMBOL = {
    "+": EX.Add,
    "-": EX.Subtract,
    "*": EX.Multiply,
    "/": EX.Divide,
}

# ----------------------------
# Load ontology (prefer local file if you create one)
# ----------------------------
g = Graph()
g.parse(data=ARITH_TTL, format="turtle")

def first_literal(subject, predicate, default=""):
    v = next(g.objects(subject, predicate), None)
    return str(v) if v is not None else default

def get_rule(op_ind):
    rule = next(g.objects(op_ind, EX.hasRule), None)
    if rule is None:
        return "No rule found for this operation."

    return (
        f"{first_literal(rule, EX.ruleName)}\n"
        f"{first_literal(rule, EX.ruleText)}\n\n"
        f"Example:\n{first_literal(rule, EX.exampleProblem)}\n"
        f"{first_literal(rule, EX.exampleSteps)}"
    )

def get_error_hint(op_ind, error_name):
    for err in g.objects(op_ind, EX.hasCommonError):
        if first_literal(err, EX.errorName) == error_name:
            return first_literal(err, EX.errorHint)
    return ""

# ----------------------------
# GUI
# ----------------------------
root = tk.Tk()
root.title("Arithmetic ITS Tutor")
root.geometry("520x380")

tk.Label(root, text="Arithmetic Intelligent Tutoring System", font=("Arial", 15, "bold")).pack(pady=10)

frm = tk.Frame(root)
frm.pack(pady=5)

tk.Label(frm, text="Number 1:").grid(row=0, column=0, padx=6, pady=6, sticky="e")
num1_entry = tk.Entry(frm, width=15)
num1_entry.grid(row=0, column=1, padx=6, pady=6)

tk.Label(frm, text="Number 2:").grid(row=1, column=0, padx=6, pady=6, sticky="e")
num2_entry = tk.Entry(frm, width=15)
num2_entry.grid(row=1, column=1, padx=6, pady=6)

tk.Label(frm, text="Operation (+ - * /):").grid(row=2, column=0, padx=6, pady=6, sticky="e")
op_entry = tk.Entry(frm, width=15)
op_entry.grid(row=2, column=1, padx=6, pady=6)

output = tk.Text(root, height=10, width=62)
output.pack(padx=12, pady=10)
output.insert("end", "Enter two numbers + an operation, then click Tutor Me.\n")
output.config(state="disabled")

def show(text):
    output.config(state="normal")
    output.delete("1.0", "end")
    output.insert("end", text)
    output.config(state="disabled")

def tutor_me():
    n1 = num1_entry.get().strip()
    n2 = num2_entry.get().strip()
    op = op_entry.get().strip()

    # Validate numbers
    try:
        a = float(n1)
        b = float(n2)
    except ValueError:
        messagebox.showwarning("Input error", "Please enter valid numbers in Number 1 and Number 2.")
        return

    # Validate operation
    if op not in OP_FROM_SYMBOL:
        # WrongOperation feedback (generic)
        msg = "Operation must be one of: +  -  *  /"
        hint = get_error_hint(EX.Add, "WrongOperation")  # reuse hint text
        messagebox.showwarning("Wrong Operation", msg + "\n\nHint:\n" + (hint or "Choose the correct operator."))
        return

    op_ind = OP_FROM_SYMBOL[op]

    # Divide by zero check
    if op == "/" and b == 0:
        hint = get_error_hint(op_ind, "DivideByZero") or "Division by zero is undefined."
        messagebox.showerror("Divide by Zero", hint)
        show(f"Error: {hint}\n\nRule:\n{get_rule(op_ind)}")
        return

    # Compute answer
    if op == "+":
        ans = a + b
    elif op == "-":
        ans = a - b
    elif op == "*":
        ans = a * b
    else:  # "/"
        ans = a / b

    rule_text = get_rule(op_ind)

    text = (
        f"Input:\n  Number 1 = {a}\n  Number 2 = {b}\n  Operation = {op}\n\n"
        f"Answer:\n  {a} {op} {b} = {ans}\n\n"
        f"--- Rule from Ontology ---\n{rule_text}\n"
    )
    show(text)

tk.Button(root, text="Tutor Me", font=("Arial", 12, "bold"), command=tutor_me).pack(pady=5)

root.mainloop()
