import com.atlassian.jira.component.ComponentAccessor
import com.atlassian.jira.config.util.JiraHome

def jiraHome = ComponentAccessor.getComponent(JiraHome)
def optionsManager = ComponentAccessor.optionsManager
def customFieldManager = ComponentAccessor.customFieldManager
def issueManager = ComponentAccessor.issueManager

log.warn("---------------------- Started option service --------------")

log.warn("Kicking Python script to download")
log.warn("/usr/bin/python /jira_home/scripts/automation/jira_picker/generate_jira_project_list.py".execute().text)

def parsedFile = new File(jiraHome.localHomePath + "/scripts/automation/jira_picker/jira_project_list").getText("UTF-8")
def textOptionsList = parsedFile.split("\n")
textOptionsList.each {
    log.warn(it)
}

def issue = issueManager.getIssueObject("JIRA-12345") //An issue with the custom field selectable
def customField = customFieldManager.getCustomFieldObjectByName("Jira Project Picker")
def fieldConfig = customField.getRelevantConfig(issue)
def existingOptions = optionsManager.getOptions(fieldConfig)

def highestSeq = existingOptions ? existingOptions*.sequence.max() : -1
highestSeq ++

// Iterate the text file, here we create new option if not present or we re-enable previously disabled options
textOptionsList.each { textOptionFromFile ->
    def existingOption = existingOptions.find {
        it.value.trim() == textOptionFromFile.trim()
    }
    //If the option is not present into the existing options then create a new option
    if(existingOption == null){
        optionsManager.createOption(fieldConfig, null as Long, highestSeq, (textOptionFromFile as String).trim())
        highestSeq++
    }
    else{
        //If the option exist but has been disabled, we re-enable it
        if(existingOption.disabled){
            optionsManager.enableOption(existingOption)
        }
    }
}

// Get the newly updated options in case there was a change
def updatedOptions = optionsManager.getOptions(fieldConfig)
// Iterate the options inside the select field, here we are checking if the options are still valid, if not we disable them
updatedOptions.each { existingOption ->
    // Find if the existing option is still inside the file
    def existingOptionPresentInsideFile = textOptionsList.find {
        it.trim() == existingOption.value.trim()
    }
    if(existingOptionPresentInsideFile == null){
        //If the option inside the select field has been removed from the file, then disable it (theoretically you should be able to still see
        // the value inside issue but it's not gonna be selectable anymore)
        optionsManager.disableOption(existingOption)
    }
}

log.warn("------- End option service ----------------")
