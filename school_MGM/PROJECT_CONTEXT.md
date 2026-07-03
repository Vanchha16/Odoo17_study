# School Management System — Project Context

## Overview

- **Module name:** `school_MGM`
- **Odoo version:** 17.0
- **Author:** Cambodian Devs Team
- **License:** AGPL-3
- **Depends:** `base`, `mail`
- **Location:** `odoo/Customize_sale_addons/school_MGM/`

A custom Odoo module for managing a school's academic structure, students, teachers, timetables, and rooms.

---

## Models

### `school.student`
Student records.

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Required, translatable |
| `dob` | Date | Date of birth |
| `email` | Char | |
| `gender` | Selection | male / female / other |
| `phone` | Char | |
| `status` | Selection | active / inactive (default: active) |
| `group_id` | Many2one → `school.group` | Required |
| `major_id` | Many2one → `school.major` | Required |
| `name_major` | Char | Related: `major_id.name`, stored |
| `name_major_code` | Char | Related: `major_id.code`, stored |
| `note` | Text | Inactive reason |
| `age` | Integer | Computed from `dob`, stored |

**Methods:**
- `_compute_age` — calculates age from `dob`
- `action_set_inactive` — opens wizard `school.inactive.student`
- `action_set_active` — clears note, sets status = active

**Inherits:** `mail.thread`

---

### `school.teacher`
Teacher records.

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Required |
| `email` | Char | Required |
| `phone` | Char | Required |
| `subject_id` | Many2many → `school.subject` | |
| `group_id` | Many2many → `school.group` | |

**Inherits:** `mail.thread`

---

### `school.major`
Academic majors.

| Field | Type | Notes |
|---|---|---|
| `code` | Char | Required, used as `_rec_name` |
| `name` | Char | Required |
| `degree_level` | Selection | bachelor / associate / master |
| `status` | Selection | active / inactive |

**`_compute_display_name`** → shows `{code} - {name}`

---

### `school.group`
Student class groups.

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Required, unique |
| `label_id` | Many2one → `school.group.label` | |
| `display_group_name` | Char | Computed: `{label}{name}`, `_rec_name` |
| `period` | Selection | Morning / Afternoon / Evening, required |
| `student_ids` | One2many → `school.student` | |
| `teacher_id` | Many2many → `school.teacher` | Required |
| `student_count` | Integer | Computed |
| `teacher_count` | Integer | Computed |

**Inherits:** `mail.thread`

---

### `school.timetable`
Weekly class schedule.

| Field | Type | Notes |
|---|---|---|
| `reference` | Char | Auto-generated sequence, readonly |
| `teacher_id` | Many2one → `school.teacher` | Required |
| `group_id` | Many2one → `school.group` | Required, domain filtered by teacher |
| `subject_id` | Many2one → `school.subject` | Required, domain filtered by teacher |
| `room_id` | Many2one → `school.room` | Required |
| `time_start` | Datetime | Required |
| `time_end` | Datetime | Required, auto-set on `time_start` change |
| `period` | Selection | Related from `group_id.period`, stored |
| `state` | Selection | draft / confirmed / cancelled |
| `notes` | Text | |

**Business logic:**
- Auto-generates reference from `ir.sequence` (`school.timetable`)
- `_onchange_time_start` — auto-sets `time_end` (+1.5h before 17:45, +1h after)
- `_check_time` — end must be after start
- `_check_overlap` — prevents double-booking of group or teacher
- Timezone-aware using `Asia/Phnom_Penh`
- States: `action_confirm`, `action_cancel`, `action_reset_draft`

**Inherits:** `mail.thread`

---

### `school.subject`
Subjects/courses.

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Required, unique |
| `sequence` | Integer | Default 10 |
| `teacher_id` | Many2many → `school.teacher` | |

**Inherits:** `mail.thread`

---

### `school.room`
Classrooms.

| Field | Type | Notes |
|---|---|---|
| `floor` | Selection | Floor 1–5, required |
| `room_code` | Selection | A–J, required |
| `room_label` | Char | Computed: `{floor}{room_code}`, `_rec_name` |
| `capacity` | Integer | |
| `sequence` | Integer | Default 10 |
| `note` | Text | |

**Constraint:** `UNIQUE(floor, room_code)`

---

### `school.subject.offering`
Links subject + major + program year + semester.

| Field | Type | Notes |
|---|---|---|
| `subject_id` | Many2one → `school.subject` | Required |
| `major_id` | Many2one → `school.major` | Required |
| `program_year_id` | Many2one → `school.program.year` | Required |
| `semester_id` | Many2one → `school.semester` | Required |
| `display_name` | Char | Computed: `code \| year \| semester \| subject` |

**Constraint:** unique combination of major + year + semester + subject

---

### `school.inactive.student` (TransientModel / Wizard)
Popup wizard to set a student inactive with a reason.

| Field | Type |
|---|---|
| `student_id` | Many2one → `school.student` |
| `note` | Text (required) |

`action_confirm` — writes `status=inactive` and `note` to the student.

---

### `manage.teacher`
Assign subjects and groups to a teacher.

| Field | Type |
|---|---|
| `teacher_id` | Many2one → `school.teacher` |
| `subject_id` | Many2many → `school.subject` |
| `group_id` | Many2many → `school.group` |

---

### Other models (referenced but not detailed)
- `school.group.label` — labels for groups (e.g. "A", "B")
- `school.academic.year` — academic years
- `school.semester` — semesters
- `school.program.year` — program years (Year 1, Year 2, etc.)

---

## Security / Access Rights

**Module category:** `SETEC School Management`

| Role | XML ID | Implies |
|---|---|---|
| Administrator | `group_school_admin` | `base.group_user` |
| Director | `group_school_dean` | `base.group_user` |
| Teacher | `group_school_teacher` | `base.group_user` |
| Student | `group_school_student` | `base.group_user` |

> All roles imply `base.group_user` (Internal User) — none use portal.
> `implied_ids` uses `(6, 0, [ref(...)])` syntax to fully replace (not just append) the implied groups on upgrade.

---

## Known Issues / Fixes Applied

### 1. `display_name` compute conflict (student.py)
**Problem:** A compute method was named `_compute_display_name`, which is reserved by Odoo's ORM for the built-in `display_name` field. The method assigned to `display_name_major` instead of `display_name`, causing:
```
ValueError: Compute method failed to assign school.student(3,).display_name
```
**Fix:** Renamed method to `_compute_display_name_major`. Field removed from final model.

---

### 2. Student role cannot be assigned to users
**Problem:** The Student group originally used `implied_ids = [(4, ref('base.group_portal'))]` (Portal), while all other roles used `base.group_user` (Internal User). Odoo enforces mutual exclusivity between Internal User and Portal, so existing internal users could not be assigned the Student role.

**Secondary problem:** Changing to `(4, ref('base.group_user'))` only ADDS the new group without removing the old `base.group_portal`. This left the Student group implying BOTH user types simultaneously.

**Fix:** Changed all `implied_ids` to `(6, 0, [ref('base.group_user')])` which fully replaces the list, removing portal and setting only internal user.

---

### 3. `tracking=True` warnings on non-mail models
Fields on `manage.teacher`, `school.room`, and `school.subject.offering` use `tracking=True` but these models do not inherit `mail.thread`. Odoo logs a WARNING for each such field at startup. These are harmless but noisy.

**Fix (not yet applied):** Either add `_inherit = ['mail.thread']` to those models, or remove `tracking=True` from their fields.

---

### 4. FontAwesome icon accessibility warnings
Multiple kanban views use `<i>` or `<span>` tags with FA icon classes but no `title` attribute. Odoo logs accessibility WARNINGs for each. These are cosmetic/non-breaking.

**Fix (not yet applied):** Add `title="..."` to each icon tag, e.g.:
```xml
<i class="fa fa-users text-primary me-2" title="Group"/>
```

---

## File Structure

```
school_MGM/
├── __manifest__.py
├── __init__.py
├── data/
│   └── sequence.xml          # ir.sequence for timetable reference
├── models/
│   ├── student.py
│   ├── teacher.py
│   ├── major.py
│   ├── group.py
│   ├── grouplabel.py
│   ├── subject.py
│   ├── room.py
│   ├── timetable.py
│   ├── inactive_student.py
│   ├── manage_teacher.py
│   ├── subject_offering.py
│   ├── academic_year.py
│   ├── semester.py
│   └── program_year.py
├── views/
│   ├── student_view.xml      # kanban, tree, form, search+searchpanel
│   ├── teacher_view.xml
│   ├── manage_teacher.xml
│   ├── group_view.xml
│   ├── subject_view.xml
│   ├── room_view.xml
│   ├── timetable.xml
│   ├── academic_year.xml
│   ├── semester.xml
│   ├── program_year.xml
│   ├── subject_offering.xml
│   ├── major_view.xml
│   └── menu.xml
├── security/
│   ├── security.xml          # groups + module category
│   └── ir.model.access.csv
└── static/src/
    ├── school_timetable.css
    └── school_student_kanban.css
```