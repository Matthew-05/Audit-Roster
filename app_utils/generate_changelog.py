def generate_changelog_html():
    changelog = """
    <div class="row">
        <div class="col s12">
            <div class="card">
                <div class="card-content">
                    <span class="card-title">To Do:</span>
                    <ul class="changelog-list">
                        <li>Add:</li>
                        <ul class="changelog-sublist">
                            <li>Add report for all engagements filted by deadline. Group by partner.</li>
                            <li>Add customizable default timeline view.</li>
                            <li>Improve staff view schedule (i.e. sort by hire date, improve aesthetics.</li>
                            <li>Implement roll-forward feature.</li>
                            <li>Add customization to save schedule (i.e. date range, specific staff)</li>
                        </ul>
                    </ul>
                    <ul class="changelog-list">
                        <li>Known bugs:</li>
                        <ul class="changelog-sublist">
                            <li>The observation modal footer buttons clip the modal content.</li>
                        </ul>
                    </ul>
                </div>
            </div>
        </div>

        <div class="col s12">
            <div class="card">
                <div class="card-content">
                    <span class="card-title">v2.0.0</span>
                    <ul class="changelog-list">
                        <li>Added:</li>
                        <ul class="changelog-sublist">
                            <li>Added schedule rollforward capability (see newly added button on the engagements tab).</li>
                        </ul>
                        <li>Fixed:</li>
                        <ul class="changelog-sublist">
                            <li>Assignments moved between employees are now correctly updated in the database.</li>
                            <li>Added override for the save schedule when it un-catestrophically fails.</li>
                        </ul>
                    </ul>
                </div>
            </div>
        </div>

        <div class="col s12">
            <div class="card">
                <div class="card-content">
                    <span class="card-title">v1.9.1</span>
                    <ul class="changelog-list">
                        <li>Fixed:</li>
                        <ul class="changelog-sublist">
                            <li>Fixed dates in the edit observation modal being a day earlier than intended.</li>
                            <li>Fixed the hire dates in the staff table being a day earlier than intended.</li>
                        </ul>
                    </ul>
                </div>
            </div>
        </div>

        <div class="col s12">
            <div class="card">
                <div class="card-content">
                    <span class="card-title">v1.9.0</span>
                    <ul class="changelog-list">
                        <li>Added:</li>
                        <ul class="changelog-sublist">
                            <li>Added scheduled observations to the generated staff view schedule.</li>
                            <li>Added CPE excel export (exports all time off entries with the description set to "CPE".).</li>
                        </ul>
                    </ul>
                </div>
            </div>
        </div>

        
        <div class="col s12">
            <div class="card">
                <div class="card-content">
                    <span class="card-title">v1.8.1</span>
                    <ul class="changelog-list">
                        <li>Fixed:</li>
                        <ul class="changelog-sublist">
                            <li>Fixed hidden observations not appearing as options in the previous observations dropdown.</li>
                            <li>Fixed set previous observations not pre-populating the dropdown option.</li>
                        </ul>
                    </ul>
                </div>
            </div>
        </div>

        <div class="col s12">
            <div class="card">
                <div class="card-content">
                    <span class="card-title">v1.8.0</span>
                    <ul class="changelog-list">
                        <li>Added:</li>
                        <ul class="changelog-sublist">
                            <li>Added a compare schedule function.</li>
                        </ul>
                    </ul>
                    <ul class="changelog-list">
                        <li>Fixed:</li>
                        <ul class="changelog-sublist">
                            <li>Fixed the prefilled deadline date in the edit engagement modal being a day before the intended date.</li>
                        </ul>
                    </ul>
                </div>
            </div>
        </div>


        <div class="col s12">
            <div class="card">
                <div class="card-content">
                    <span class="card-title">v1.7.2</span>
                    <ul class="changelog-list">
                        <li>Modified:</li>
                        <ul class="changelog-sublist">
                            <li>Removed unecessary restriction on new engagement modal submission (deadline).</li>
                            <li>Added Partner's name to the observation table.</li>
                            <li>Standardized all date pickers to start on sunday.</li>
                        </ul>
                    </ul>
                </div>
            </div>
        </div>

        <div class="col s12">
            <div class="card">
                <div class="card-content">
                    <span class="card-title">v1.7.1</span>
                    <ul class="changelog-list">
                        <li>Added:</li>
                        <ul class="changelog-sublist">
                            <li>Added ability to hide certain observations from the table.</li>
                        </ul>
                    </ul>
                    <ul class="changelog-list">
                        <li>Modified:</li>
                        <ul class="changelog-sublist">
                            <li>Removed the deadline column in the observations table.</li>
                        </ul>
                    </ul>
                </div>
            </div>
        </div>

        <div class="col s12">
            <div class="card">
                <div class="card-content">
                    <span class="card-title">v1.7.0</span>
                    <ul class="changelog-list">
                        <li>Added:</li>
                        <ul class="changelog-sublist">
                            <li>Added success message when creating a new engagement.</li>
                            <li>Added ability to edit unassigned engagements from the unassigned engagement list.</li>
                            <li>Added reporting period distinction to engagements in the observations.</li>
                        </ul>
                    </ul>
                    <ul class="changelog-list">
                        <li>Modified:</li>
                        <ul class="changelog-sublist">
                            <li>Revamped changelog styling.</li>
                        </ul>
                    </ul>
                    <ul class="changelog-list">
                        <li>Fixed:</li>
                        <ul class="changelog-sublist">
                            <li>Fixed error caused by trying to edit existing engagement's reporting period.</li>
                        </ul>
                    </ul>
                </div>
            </div>
        </div>

        <div class="col s12">
            <div class="card">
                <div class="card-content">
                    <span class="card-title">v1.6.2</span>
                    <ul class="changelog-list">
                        <li>Modified:</li>
                        <ul class="changelog-sublist">
                            <li>Modified the unassigned engagements list in the sidebar to also show the Partner & Reporting Period.</li>
                        </ul>
                    </ul>
                </div>
            </div>
        </div>

        <div class="col s12">
            <div class="card">
                <div class="card-content">
                    <span class="card-title">v1.6.1</span>
                    <ul class="changelog-list">
                        <li>Modified:</li>
                        <ul class="changelog-sublist">
                            <li>Modified concurrent engagements to show it by partner.</li>
                        </ul>
                    </ul>
                    <ul class="changelog-list">
                        <li>Fixed:</li>
                        <ul class="changelog-sublist">
                            <li>Fixed edit engagement modal not prepopulating the reporting period correctly.</li>
                            <li>Fixed the generate selected reports modal only being able to show 3 tabs, even if more than 3 reports are run.</li>
                        </ul>
                    </ul>
                </div>
            </div>
        </div>

        <div class="col s12">
            <div class="card">
                <div class="card-content">
                    <span class="card-title">v1.6.0</span>
                    <ul class="changelog-list">
                        <li>Added:</li>
                        <ul class="changelog-sublist">
                            <li>Added ability to edit assignment and associated engagement by double clicking the assignment.</li>
                            <li>Added login/logout capability</li>        
                        </ul>
                    </ul>
                    <ul class="changelog-list">
                        <li>Fixed:</li>
                        <ul class="changelog-sublist">
                            <li>Fixed the database download and partner engagement download not saving to the correct directory.</li>
                            <li>Fixed a bug where the right click add on the schedule did work properly</li>
                        </ul>
                    </ul>
                </div>
            </div>
        </div>

        <div class="col s12">
            <div class="card">
                <div class="card-content">
                    <span class="card-title">v1.5.0</span>
                    <ul class="changelog-list">
                        <li>Added:</li>
                        <ul class="changelog-sublist">
                            <li>Added a concurrent user warning.</li>
                            <li>Added ability to add outside firm observers for an observation.</li>
                        </ul>
                    </ul>
                    <ul class="changelog-list">
                        <li>Modified:</li>
                        <ul class="changelog-sublist">
                            <li>Improved the employee view downloaded schedule.</li>
                        </ul>
                    </ul>
                    <ul class="changelog-list">
                        <li>Fixed:</li>
                        <ul class="changelog-sublist">
                            <li>Fixed bug where selecting an engagement for a new observation resulted in an error.</li>
                        </ul>
                    </ul>
                </div>
            </div>
        </div>

        <div class="col s12">
            <div class="card">
                <div class="card-content">
                    <span class="card-title">v1.4.1</span>
                    <ul class="changelog-list">
                        <li>Modified:</li>
                        <ul class="changelog-sublist">
                            <li>Changed d/L -> DL.</li>
                        </ul>
                    </ul>
                    <ul class="changelog-list">
                        <li>Fixed:</li>
                        <ul class="changelog-sublist">
                            <li>Fixed starting a save report dialog, closing it, and then attempting to start a save report dialog failing.</li>
                        </ul>
                    </ul>
                </div>
            </div>
        </div>

        <div class="col s12">
            <div class="card">
                <div class="card-content">
                    <span class="card-title">v1.4.0</span>
                    <ul class="changelog-list">
                        <li>Added:</li>
                        <ul class="changelog-sublist">
                            <li>Implemented ability to filter out inactive staff from the schedule viewer/editor.</li>
                            <li>Implemented ability to filter out inactive staff from saved schedule.</li>
                            <li>Experimental: Added new styling to the assignment items.</li>
                            <li>Added a partner engagement report.</li>
                            <li>Added deadline heatmap report.</li>
                        </ul>
                    </ul>
                    <ul class="changelog-list">
                        <li>Modified:</li>
                        <ul class="changelog-sublist">
                            <li>Added success & failure messages where they should've been implemented originally.</li>
                            <li>Fully phased out materialize datepickers and replaced with the superior litepicker datepickers.</li>
                            <li>Changed order of columns in the engagement table.</li>
                        </ul>
                    </ul>
                    <ul class="changelog-list">
                        <li>Fixed:</li>
                        <ul class="changelog-sublist">
                            <li>Fixed certain inconsistencies and bugs regarding the schedule refresh function.</li>
                            <li>Fixed inability to delete employees & partners.</li>
                            <li>Fixed an issue if the program started and the database path specified in settings is unable to be accessed.</li>
                            <li>Fixed first time start logic resulting in crash.</li>
                        </ul>
                    </ul>
                </div>
            </div>
        </div>

        <div class="col s12">
            <div class="card">
                <div class="card-content">
                    <span class="card-title">v1.3.1</span>
                    <ul class="changelog-list">
                        <li>Added:</li>
                        <ul class="changelog-sublist">
                            <li>Added new "Fiscal Year" field to engagement database model (as well as updated needed areas)</li>
                        </ul>
                    </ul>
                    <ul class="changelog-list">
                        <li>Fixed:</li>
                        <ul class="changelog-sublist">
                            <li>Fixed add new engagement modal's datepicker not triggering.</li>
                        </ul>
                    </ul>
                </div>
            </div>
        </div>

        <div class="col s12">
            <div class="card">
                <div class="card-content">
                    <span class="card-title">v1.3.0</span>
                    <ul class="changelog-list">
                        <li>Added:</li>
                        <ul class="changelog-sublist">
                            <li>Implemented database migration capability.</li>
                            <li>Added new partner table & associated functionality.</li>
                            <li>Reflected newly added data to the schedule viewed assignments.</li>
                            <li>Added first report (concurrent engagements over time). (More to come).</li>
                            <li>Added walkthrough schedule / planned out assignment schedule.</li>
                        </ul>
                    </ul>
                    <ul class="changelog-list">
                        <li>Fixed:</li>
                        <ul class="changelog-sublist">
                            <li>Fixed changelog modal formatting.</li>
                        </ul>
                    </ul>
                </div>
            </div>
        </div>

        <div class="col s12">
            <div class="card">
                <div class="card-content">
                    <span class="card-title">v1.2.0</span>
                    <ul class="changelog-list">
                        <li>Added:</li>
                        <ul class="changelog-sublist">
                            <li>Users can now add assignments by double clicking where they want it to start</li>
                            <li>Added version update notifier and changelog.</li>
                            <li>Added ability to differentiate between engagement types in bulk add/single add.</li>
                            <li>Made the sidebar collapsable.</li>
                            <li>Added hover tooltip for assignments.</li>
                            <li>Added unassigned engagements list to sidebar when on schedule page.</li>
                        </ul>
                    </ul>
                    <ul class="changelog-list">
                        <li>Fixed:</li>
                        <ul class="changelog-sublist">
                            <li>Fixed bug where trying to add an assignment after adding one already resulted in unintended duplicate behavior.</li>
                        </ul>
                    </ul>
                </div>
            </div>
        </div>

        <div class="col s12">
            <div class="card">
                <div class="card-content">
                    <span class="card-title">v1.1.1</span>
                    <ul class="changelog-list">
                        <li>Adjusted width of the timeline.</li>
                        <li>Removed "time off" label.</li>
                        <li>Renamed items as "Time Off / CPE."</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    """
    return changelog
