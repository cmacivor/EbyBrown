# Added by Yogini Marathe
# Dec-04-2020
# PowerShell script to monitor the TCP Socket tasks and Start if required.

# Monitor if server scheduled task is running
## Takethe parameters
$taskNames = $args
while(1){ ## Run always
    foreach ($taskName in $taskNames)
    {
        Write-Output $taskName
        try{
            $splitTaskName = $taskName.split("\")[-1]
            $task = Get-ScheduledTask -TaskName $splitTaskName -ErrorAction Stop #if error occurs it will be sent to catch
            $taskState = $task.State
            if ($taskState -eq 'Running'){
                Write-Output $taskState
            }
            else{
                $taskPath = $taskName #"\" +
                Write-output 'Task ' $taskName ' is Not Running, attempting to start the task'
                Start-ScheduledTask -TaskName $taskPath -ErrorAction Stop
            }
        }catch{
            Write-output $_.Exception.Message
        }

    }
    Start-Sleep -s 60
}