from flask import render_template
from datetime import datetime
import json
import os


def save_schedule(employees, assignments, time_off, observations, version, save_directory):

    current_datetime = datetime.now().strftime('%m/%d/%Y %I:%M %p')
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Saved Schedule - {current_datetime}</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css" rel="stylesheet" type="text/css" />
        <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.1/moment.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script>
            <link
      href="https://cdn.jsdelivr.net/npm/simple-datatables@latest/dist/style.css"
      rel="stylesheet"
      type="text/css"
    />
    <script
      src="https://cdn.jsdelivr.net/npm/simple-datatables@latest"
      type="text/javascript"
    ></script>
        <style>
            .vis-time-axis .vis-grid.vis-minor {{
                border-width: 1px;
                border-color: #e0e0e0;
            }}
            .vis-time-axis .vis-grid.vis-saturday,
            .vis-time-axis .vis-grid.vis-sunday {{
                background-color: #f0f0f0;
            }}
            .vis-time-axis .vis-grid.vis-monday {{
                border-width: 3px;
                border-color: #a0a0a0;
            }}
            .vis-time-axis .vis-text.vis-major {{
                font-weight: bold;
            }}
            .hire-date {{
                font-size: 0.8em;
                color: #666;
            }}
            .vis-item.time-off-item {{
                background-color: orange;
                border-color: darkorange;
                color: white;
                font-weight: bold;
            }}
            .current-week-overlay {{
                background-color: rgba(255, 252, 61, 0.2);
            }}
            .hire-date {{
font-size: 0.8em;
color: #666;
}}

.vis-item.time-off-item {{
background-color: orange;
border-color: darkorange;
color: white;
font-weight: bold;
}}
#timeline {{
    height: 600px;
}}
  .highlighted-assignment {{
    border: 2px solid #ff4081 !important;
    background-color: rgba(255, 64, 129, 0.2) !important;
    z-index: 1;
  }}
  .version-info {{
        position: fixed;
        bottom: 10px;
        right: 10px;
        background-color: rgba(0, 0, 0, 0.5);
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 12px;
        z-index: 1000;
      }}
      .engagement-main-info {{
    background-color: #fffae0;
    padding: 3px;
    border-radius: 4px;
}}
.engagement-partner {{
    background-color: #aabaff;
    padding: 3px;
    border-radius: 4px;
}}
.engagement-deadline {{
    background-color: #ffa9ea;
    padding: 3px;
    border-radius: 4px;
}}

.engagement-main-info,
.engagement-partner,
.engagement-deadline {{
    margin-right: 5px;
}}
.employee-filter-container {{
    max-height: 500px;
    overflow-y: auto;
    border: 1px solid #ddd;
    padding: 10px;
    margin-bottom: 10px;
}}

.employee-checkbox-wrapper {{
    display: block;
    margin-bottom: 10px;
}}
nav {{
display: none;
}}
  .datatable-dropdown {{
    display: none;
  }}
        </style>
    </head>
    <body>
     <div class="version-info">v{ version }</div>
<div class="">
    <p style="padding: 0 .75rem;">Schedule saved on: {current_datetime}</p>
    <div class="row">
        <div class="col s3">
            <div class="input-field">
                <input type="text" id="engagementFilter" class="autocomplete" placeholder="Filter by Engagement">
            </div>
            <div class="employee-filter-container">
                <p>
                    <label>
                        <input type="checkbox" class="filled-in" id="checkAllEmployees" checked>
                        <span>Select All</span>
                    </label>
                </p>
                <div id="employeeFilter"></div>
            </div>
        </div>
<div class="col s9">
    <ul class="tabs">
        <li class="tab"><a href="#timeline">Schedule</a></li>
        <li class="tab"><a href="#observations-tab">Observations</a></li>
    </ul>
    <div id="timeline"></div>
    <div id="observations-tab">
        <table id="observations-table" class="display">
            <thead>
                <tr>
                    <th>Engagement</th>
                    <th>Reporting Period</th>
                    <th>Partner</th>
                    <th>Scheduler</th>
                    <th>Observer</th>
                    <th>Scheduled Date</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    </div>
</div>
    </div>
</div>
        <script>
            const employees = {json.dumps(employees)};
            const assignments = {json.dumps(assignments)};
            const timeOff = {json.dumps(time_off)};
            const observations = {json.dumps(observations)};

                    // Initialize observations table
let observationsTable = new simpleDatatables.DataTable("#observations-table", {{
    data: {{
    paging: false,
        headings: [
            "Engagement",
            "Reporting Period",
            "Partner",
            "Scheduler",
            "Observer",
            "Scheduled Date",
        ],
                data: observations
            .sort((a, b) => {{
                // Handle null dates by putting them at the end
                if (!a.scheduled_observation_date) return 1;
                if (!b.scheduled_observation_date) return -1;
                return new Date(a.scheduled_observation_date) - new Date(b.scheduled_observation_date);
            }}).map(o => [
            o.engagement_title,
            o.reporting_period || '<span class="grey-text">Not Set</span>',
            o.partner_name || '<span class="grey-text">Not Set</span>',
            o.scheduler_name || '<span class="red-text">Not Assigned</span>',
            o.observer_name || '<span class="red-text">Not Assigned</span>',
            o.scheduled_observation_date || '<span class="red-text">Not Scheduled</span>'
        ])
    }}
}});

 
            let allGroups = employees.map((employee, index) => {{
                const hireDate = new Date(employee.hire_date);
                hireDate.setDate(hireDate.getDate() + 1);
                return {{
                    id: employee.id,
                    content: `<div>${{employee.first_name}} ${{employee.last_name}}</div><div class="hire-date">${{hireDate.toLocaleDateString()}}</div>`,
                    hireDate: hireDate,
                    order: index
                }};
            }});

            allGroups.sort((a, b) => a.hireDate - b.hireDate);

            // Update the order after sorting
            allGroups = allGroups.map((group, index) => ({{
                ...group,
                order: index
            }}));

            

            let allItems = assignments.map(assignment => {{
                const startDate = new Date(assignment.start_date + "T00:00:00");
                const endDate = new Date(assignment.end_date + "T23:59:59");

                return {{
                    id: assignment.id,
                    group: assignment.employee_id,
                    content: `
                        <div class="engagement-info-container">
                            <span class="engagement-main-info">
                                ${{assignment.engagement_title}} - ${{assignment.fiscal_year || "N/A"}} - ${{assignment.engagement_type}}
                            </span>
                            <span class="engagement-partner">
                                ${{assignment.partner_initials || "N/A"}}
                            </span>
                            <span class="engagement-deadline">
                                DL ${{assignment.deadline || "N/A"}}
                            </span>
                        </div>
                    `,
                    start: startDate,
                    end: endDate,
                    order: 2,
                }};
            }});

            timeOff.forEach(item => {{
            console.log(item);
                allItems.push({{
id: `timeoff_${{item.id}}`,
group: item.employee_id,
content: `${{item.description}}`,
start: new Date(item.start_date + "T00:00:00"),
end: new Date(item.end_date + "T23:59:59"),
className: "time-off-item",
order: 1, // This ensures time off items are at the top
                }});
            }});

            const today = new Date();
            const startOfWeek = new Date(today);
            startOfWeek.setDate(today.getDate() - ((today.getDay() + 6) % 7));
            startOfWeek.setHours(0, 0, 0, 0);

            const endOfWeek = new Date(startOfWeek);
            endOfWeek.setDate(startOfWeek.getDate() + 6);
            endOfWeek.setHours(23, 59, 59, 999);

            allItems.push({{
                id: "current-week",
                start: startOfWeek,
                end: endOfWeek,
                type: "background",
                className: "current-week-overlay",
            }});

            const container = document.getElementById("timeline");
            const options = {{
order: function (a, b) {{
            return a.order - b.order;
          }},
                groupOrder: 'order',  
                editable: false,
                height: '800px',
                width: '100%',
                verticalScroll: true,
                orientation: {{
                    axis: "top",
                    item: "top",
                }},
                margin: {{
                    item: {{
                        vertical: 10,
                    }},
                }},
                timeAxis: {{ scale: "day", step: 1 }},
                format: {{
                    minorLabels: function (date, scale, step) {{
                        switch (scale) {{
                            case "day":
                                return moment(date).format("D");
                            case "week":
                                const weekStart = moment(date).startOf("week");
                                const weekEnd = moment(date).endOf("week");
                                return `${{weekStart.format("MMM D")}} - ${{weekEnd.format("D")}}`;
                            case "month":
                                return moment(date).format("MMM");
                            default:
                                return "";
                        }}
                    }},
                    majorLabels: function (date, scale, step) {{
                        switch (scale) {{
                            case "day":
                            case "week":
                                return moment(date).format("MMMM YYYY");
                            case "month":
                                return moment(date).format("YYYY");
                            default:
                                return "";
                        }}
                    }},
                }},
                zoomMin: 1000 * 60 * 60 * 24,
            }};

            const timeline = new vis.Timeline(container, allItems, allGroups, options);
            timeline.setWindow(startOfWeek, endOfWeek);
            // Set initial zoom to current 3 weeks
setTimeout(function() {{
    var today = new Date();
    var oneWeekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    var oneWeekLater = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
    timeline.setWindow(oneWeekAgo, oneWeekLater, {{
        animation: {{
            duration: 1000,
            easingFunction: "easeInOutQuad"
        }}
    }});
}}, 100);



            timeline.on("rangechange", function (properties) {{
                const msPerDay = 24 * 60 * 60 * 1000;
                const daysVisible = (properties.end - properties.start) / msPerDay;

                let newScale, newStep;
                if (daysVisible > 180) {{
                    newScale = "month";
                    newStep = 1;
                }} else if (daysVisible > 60) {{
                    newScale = "week";
                    newStep = 1;
                }} else {{
                    newScale = "day";
                    newStep = 1;
                }}

                if (newScale !== timeline.timeAxis.scale) {{
                    timeline.setOptions({{
                        timeAxis: {{ scale: newScale, step: newStep }},
                    }});
                }}
            }});


function filterSchedule() {{
    const checkedEmployees = Array.from(document.querySelectorAll('.filled-in:checked')).map(cb => parseInt(cb.value));
    const engagementText = document.getElementById("engagementFilter").value.toLowerCase();
    
    // Filter timeline
    let filteredGroups = allGroups;
    if (checkedEmployees.length > 0) {{
        filteredGroups = allGroups.filter(group => checkedEmployees.includes(group.id));
    }}

    let filteredItems = allItems.filter(item => {{
        const matchesEmployee = checkedEmployees.length === 0 || checkedEmployees.includes(item.group);
        const matchesEngagement = !engagementText || (item.content && item.content.toLowerCase().includes(engagementText));
        return matchesEmployee && matchesEngagement;
    }});

    timeline.setData({{ items: filteredItems, groups: filteredGroups }});

}}



function createEmployeeCheckboxes() {{
    const container = document.getElementById('employeeFilter');
    allGroups.forEach(group => {{
        const wrapper = document.createElement('p');
        wrapper.className = 'employee-checkbox-wrapper';

        const label = document.createElement('label');
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `employee-${{group.id}}`;
        checkbox.value = group.id;
        checkbox.className = 'filled-in';
        checkbox.checked = true;
        checkbox.addEventListener('change', filterSchedule);

        const span = document.createElement('span');
        const name = group.content.match(/<div>(.*?)<\/div>/)[1];


        console.log(name);
        span.textContent = name;

        label.appendChild(checkbox);
        label.appendChild(span);
        wrapper.appendChild(label);
        container.appendChild(wrapper);
    }});

    document.getElementById('checkAllEmployees').addEventListener('change', function() {{
        const isChecked = this.checked;
        document.querySelectorAll('.employee-checkbox-wrapper input[type="checkbox"]').forEach(cb => {{
            cb.checked = isChecked;
        }});
        filterSchedule();
    }});

    M.updateTextFields();
    filterSchedule();
}}






    createEmployeeCheckboxes();


function filterItem(item, engagementText, filteredGroups) {{
    if (item.className == "current-week-overlay") {{
        return true;
    }}
    const matchesEngagement =
        !engagementText || (item.content && item.content.toLowerCase().includes(engagementText));
    const matchesEmployee = filteredGroups.some(
        (group) => group.id == item.group
    );
    return matchesEngagement && matchesEmployee;
}}



        timeline.on("select", function (properties) {{
          if (properties.items.length > 0) {{
            const selectedItem = timeline.itemsData.get(properties.items[0]);
            const selectedEngagement = selectedItem.content;

            allItems.forEach((item) => {{
              if (item.content === selectedEngagement) {{
                timeline.itemsData.update({{
                  id: item.id,
                  className: (item.className || "") + " highlighted-assignment",
                }});
              }} else {{
                // Preserve the "time-off-item" class if it exists
                const updatedClassName =
                  item.className && item.className.includes("time-off-item")
                    ? "time-off-item"
                    : "";
                timeline.itemsData.update({{
                  id: item.id,
                  className: updatedClassName,
                }});
              }}
            }});
          }} else {{
                allItems.forEach(item => {{
                    const updatedClassName = item.className && item.className.includes("time-off-item")
                        ? "time-off-item"
                        : "";
                    timeline.itemsData.update({{
                        id: item.id,
                        className: updatedClassName
                    }});
                }});
            }}

            timeline.redraw();
        }});
        document.getElementById("engagementFilter").addEventListener("input", filterSchedule);
        document.getElementById("engagementFilter").addEventListener("change", filterSchedule);
        


// Initialize tabs
document.addEventListener('DOMContentLoaded', function() {{
    var tabs = document.querySelectorAll('.tabs');
    M.Tabs.init(tabs);
}});
        </script>
    </body>
    </html>
    """

    current_datetime = datetime.now().strftime("%B-%d-%Y %I-%M-%p")
    file_name = f"Staff Schedule as of {current_datetime}.html"


    full_path = os.path.join(save_directory, file_name) if save_directory else file_name
    
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return {"success": True, "filename": full_path}

