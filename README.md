
<a id="readme-top"></a>

<h3 align="center">Software Architecture & Design (D780)</h3>

  <p align="center">
    Course D780 – Tasks 1 & 2  
    <br />
    <br />
</div>



## About the Project

This project was completed for **D780 – Software Architecture & Design**, a WGU course focused on the principles of software design patterns and architectural styles. The course emphasizes understanding how to identify, refactor, and justify design and architectural choices that improve scalability, flexibility, and maintainability of enterprise applications.

Throughout both tasks, I analyzed provided codebases, identified existing design or architectural patterns, evaluated their inefficiencies, and refactored them to implement more appropriate and modern solutions. The deliverables demonstrate proficiency in object-oriented design, microservices architecture, and the transition from monolithic to distributed systems.



## Course Information

**Course:** D780 – Software Architecture & Design
**Focus:** Applying design and architectural patterns to create scalable, maintainable, and modular software systems.

### Competencies

**Software Design Patterns**
The graduate applies design patterns to solve recurring software design challenges and improve system structure and behavior.

**Software Architecture Patterns**
The graduate applies architectural patterns to design scalable and maintainable system architectures.

**Refactoring and Evaluation**
The graduate analyzes existing systems, identifies inefficiencies, and refactors them to align with modern design and architectural standards.



## Task 1 – Design Patterns

Task 1 focused on analyzing and improving three provided Python components (Cart, Payment, and Inventory).
Each snippet was evaluated to identify the original design pattern, explain its inefficiencies in context, and implement a more suitable alternative.

### Highlights

* **Cart Component**

  * **Original Pattern:** Singleton
  * **Improved Pattern:** Repository
  * **Justification:** Enables per-user carts, persistence, distributed operation, and testability.

* **Payment Component**

  * **Original Pattern:** Simple Factory
  * **Improved Pattern:** Strategy
  * **Justification:** Improves extensibility, supports new gateways without modifying core logic.

* **Inventory Component**

  * **Original Pattern:** Strategy
  * **Improved Pattern:** Façade
  * **Justification:** Centralizes validation, ensures consistency, and supports transaction integrity.

Each implementation was fully commented to explain the reasoning behind structural changes and the applied pattern principles.

**Repository Branch:**
[`task-1`](https://gitlab.com/wgu-gitlab-environment/student-repos/aalcid/d780-software-architecture-and-design/-/tree/f68cfe6af6c1fefb0e60c75382e16db33516cde7)



## Task 2 – Software Architecture

Task 2 expanded to architectural-level analysis, applying architectural patterns to business scenarios and transforming a monolithic system into microservices.

### Highlights

* **Architectural Pattern Selection:**
  Identified and justified the use of **Microservices** and **Event-Driven** architectures for scalability and resilience.
  Evaluated tradeoffs between **on-premises** and **cloud** deployments, recommending cloud-first adoption for elasticity and global availability.

* **Monolithic Refactoring:**

  * Original “Retail System” was tightly coupled within a single process.
  * Refactored into independent microservices:

    * `cart_service.py`
    * `inventory_service.py`
    * `payment_service.py`
    * `orchestrator_service.py` (handles inter-service coordination)

* **Architecture Advantages:**

  * Independent scalability and deployment
  * Fault isolation and maintainability
  * Cloud-native suitability for retail, ticketing, and order-processing use cases

**Repository Branch:**
[`working-task-2`](https://gitlab.com/wgu-gitlab-environment/student-repos/aalcid/d780-software-architecture-and-design/-/tree/2a99b432300a9a9e5c5cb28d4162c3d5d9318664/)

**Demonstration Video:**
[Panopto Recording](https://wgu.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=988f4bf2-e1ca-4775-84a9-b35901011e98)


## Technology Stack

* **Language:** Python 3.10+
* **Architecture:** Microservices with REST orchestration
* **Tools:** GitLab CI/CD, UML diagrams, Panopto video demonstration


## Contact

**Silver Alcid**
[Website](https://silveralcid.com) • [Outlook](mailto:silveralcid@outlook.com)
