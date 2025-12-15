# EC2 and ECS Setup – Remote Job Portal

This document explains how **AWS EC2 (Elastic Compute Cloud)** and **AWS ECS (Elastic Container Service)** were used to host and manage the backend services of the Remote Job Portal. The compute layer is a critical part of the system, as it handles all application logic such as job posting, application processing, authentication, and integration with analytics services.

---

## Purpose of the Compute Layer

The Remote Job Portal requires a reliable and scalable execution environment that can:
- Handle multiple user requests simultaneously
- Support backend APIs and business logic
- Scale based on demand
- Integrate securely with storage, monitoring, and analytics services

To meet these requirements, EC2 and ECS were chosen as the core compute services.

---

## What Services Are Used

### Amazon EC2
EC2 provides virtual servers that act as the underlying compute infrastructure. These instances supply CPU, memory, and networking resources required to run containerized applications.

### Amazon ECS
ECS is used to manage and orchestrate containers that run the backend application. It ensures that the required number of application instances are always running and restarts containers automatically if failures occur.

---

## How the Setup Was Created

1. **EC2 Instance Creation**
   - EC2 instances were launched using Amazon Linux.
   - Appropriate instance types were selected based on expected workload.
   - Security groups were configured to allow only required traffic.

2. **ECS Cluster Creation**
   - An ECS cluster was created to manage containers.
   - EC2 instances were registered with the ECS cluster.
   - Cluster capacity was defined to support current and future load.

3. **Application Containerization**
   - The backend application was packaged into a Docker container.
   - A task definition was created specifying CPU, memory, ports, and logging.
   - Environment variables and secrets were configured securely.

4. **Service Configuration**
   - ECS services were defined to maintain the desired number of running tasks.
   - Load balancer integration ensured traffic routing to healthy containers.

---

## Access Points and Connectivity

- The **public access point** for users is the load balancer DNS.
- ECS tasks and EC2 instances are not directly exposed to the internet.
- Internal communication happens securely through AWS networking.
- IAM roles control access between ECS, S3, CloudWatch, and Secrets Manager.

This design improves security by isolating compute resources from direct public access.

---

## Advantages of Using EC2 and ECS

- Automatic recovery and self-healing
- Horizontal scalability
- Consistent runtime environment using containers
- Reduced operational overhead
- Seamless integration with AWS services

---

## Limitations and Considerations

- Requires careful resource sizing to control costs
- Container debugging can be complex initially
- Proper monitoring is essential to avoid over-provisioning

---

## Conclusion

The EC2 and ECS setup provides a **robust, scalable, and secure compute foundation** for the Remote Job Portal. By combining EC2’s flexibility with ECS’s orchestration capabilities, the system achieves high availability, operational efficiency, and production readiness. This approach reflects real-world cloud deployment practices and supports both academic evaluation and future system expansion.
# Application Hosting

The backend application is hosted on AWS-managed servers.

## Services Used
- EC2: Virtual machines
- ECS: Container management

## Benefits
- Automatic scaling
- High availability
- Secure infrastructure

