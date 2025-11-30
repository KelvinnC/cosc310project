# Sprint 3: Core Features & Milestone 3
**Sprint Duration:** October 22 - November 17, 2025  
**Sprint Goal:** Implement core backend features, achieve high test coverage, and complete Milestone 3

---

## Meeting Date: 2025-10-22
**Type of Meeting:** In-person Scrum
**Meeting Length:** 11:00-11:45
**Attendees:** Everyone

### Action Items
- Assign coding tasks as we lead up to M3 submission. 
- Review the code produced over the past week.
- Team learning session

### Meeting Notes
Went over our user stories and assigned tasks based on dependencies/blockers. We aligned our schedule expectations, hoping to get a majority of the M3 submission done before reading week. 

### Responsibilities
- Brad - US-01, 02 (user registration/verification)
- Duncan - US-03, 04, 05 (managing reviews)
- Kelvin - US-11 (sorting and filtering reviews)
- Will - US-13 (review battles)

---

## Meeting Date: 2025-10-27
**Type of Meeting:** In-person Scrum
**Meeting Length:** 14:00-15:30
**Attendees:** Everyone

### Action Items
- Discussed individual progress
- Found solution for loading reviews as this was an issue
- Discussed next steps
- Met with TA

### Meeting Notes
- All members showed what they were working on. Discussed with TA how to handle load issues with large reviews.json dataset. Planned next meeting.

### Responsibilities
- Brad - US-01, 02 (user registration/verification)
- Duncan - US-03, 04, 05 (managing reviews)
- Kelvin - US-11 (sorting and filtering reviews)
- Will - US-13 (review battles)

---

## Meeting Date: 2025-10-29
**Type of Meeting:** In-person Scrum
**Meeting Length:** 11:00-11:40
**Attendees:** Everyone

### Action Items
- Discussed progress of current tasks, review of completed tasks
- Assigned next tasks
- Reviewed and revised style guide
- M3 expectations

### Meeting Notes
- Review battles completed, pull request waiting for review
- Login, auth, and admin penalties completed, waiting for review
- Reviews basic CRUD endpoints still in progress, should be complete by 2025-10-31
- Reviewed searching for movies, pending completion by tomorrow, sorting in progress next

### Responsibilities
- Brad - US-16 (admin dashboard)
- Duncan - US-03, 04, 05 (managing reviews)
- Kelvin - US-11 (sorting and filtering reviews)
- Will - US-13, US-07 (review voting & flagging)

---

## Meeting Date: 2025-11-12
**Type of Meeting:** Virtual Scrum (Discord)
**Meeting Length:** 18:00-20:00
**Attendees:** Everyone

### Action Items
- Merge battles and reviews features to unblock dependent work
- Fix unmocked test causing database writes during test runs
- Coordinate flag system implementation to avoid duplication

### Key Discussion Points
- PR #95 approval needed to unblock US-07 and US-19
- Flag system architecture using repository pattern
- Overlap between US-07 (user flagging) and US-08 (admin dashboard)
- Bug #119: Review #3 being modified during tests causing merge conflicts

### Meeting Notes
Coordinated on merging critical features. Will identified and fixed unmocked vote test that was causing database modifications. Team divided flag-related user stories to minimize overlap. Brad working on admin flag dashboard, Will on user flag functionality. Duncan assigned US-14 for review scores.

### Responsibilities
- Brad - US-08 (admin flag dashboard)
- Duncan - US-14 (review scores)
- Kelvin - US-11 (sorting PRs awaiting review)
- Will - US-07, US-19 (review flagging)

---

## Meeting Date: 2025-11-15
**Type of Meeting:** Virtual Scrum (Discord)
**Meeting Length:** 21:00-22:30
**Attendees:** Everyone

### Action Items
- Address review update schema constraints
- Complete refactoring PRs (5 per member requirement)
- Review Kelvin's sorting PRs before weekend
- Push to complete user stories before Thursday deadline

### Key Discussion Points
- Review body character limit conflicts with existing data (>1000 chars)
- UpdateReview schema field optionality discussion
- Refactoring load_all() would require large scope changes
- Brad working on admin hide reviews functionality

### Meeting Notes
Discussed schema constraint issues with review updates. Decided to keep constraints as-is since they only apply to API operations, not existing JSON data. Team working toward 5 refactors each. Will submitted index helper refactor, Brad submitted user service refactor. Kelvin requested reviews on sorting PRs due to limited weekend availability.

### Responsibilities
- Brad - US-08 completion (admin hide reviews), refactoring
- Duncan - Complete assigned user story
- Kelvin - US-11 sorting PRs, resolve merge conflicts
- Will - Review PRs, refactoring work

---

## Meeting Date: 2025-11-17
**Type of Meeting:** Lab Check-in
**Meeting Length:** 14:00-16:00
**Attendees:** Everyone

### Action Items
- Demo M3 core features to TA
- Validate 96% test coverage achievement
- Discuss final touches before submission

### Key Discussion Points
- M3 core functionality complete
- External API integration is M4 requirement (not M3)
- Test coverage at 96%
- Review visibility implementation using load_invisible parameter

### Meeting Notes
Confirmed M3 core features working and ready for demo. Brad implemented review hiding with load_invisible boolean parameter in load_all() to minimize refactoring. Team ahead of schedule with most requirements met. Discussed that TMDB API integration can wait until M4.

### Responsibilities
- All - Final testing and documentation for M3 submission
