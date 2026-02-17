Attribute VB_Name = "Module1"
Sub NextNonZeroInColB()
' look for the next non-zero value in col B
' or an empty cell
    Dim cel As Range, startCell As Range
    Set startCell = Range("B" & ActiveCell.Row + 1)
    
    For Each cel In startCell.Parent.Range(startCell, startCell.Parent.Cells(startCell.Parent.Rows.Count, "B"))
        If cel.Value < -1 Or IsEmpty(cel.Value) Then
            ' MsgBox "cell: " & cel.Address & " is <" & cel.Value & ">", vbInformation
            cel.Select
            Exit Sub
        End If
    Next cel
    
End Sub

 
 Sub InsertMissingRow()
Attribute InsertMissingRow.VB_ProcData.VB_Invoke_Func = " \n14"
'
' Insert Empty Missing Row Macro and fix date/time progression
' Keyboard Shortcut: Ctrl+Shift+I
'
    ' start with the active Cell in column B
    ' Insert a new row above the active row
    ActiveCell.EntireRow.Insert Shift:=xlDown, CopyOrigin:=xlFormatFromLeftOrAbove
    
    ' reset the activeCell to the new row, column A
    ActiveCell.Offset(0, -1).Select
    With ActiveCell
    
        ' Copy A:C relative formulas from the row above into the new row
        .Offset(-1, 0).Range("A1:C1").Copy
        .Range("A1:C2").PasteSpecial xlPasteFormulas
    
        ' Set column D in the new row = previous time + 30 minutes
        .Range("D1").FormulaR1C1 = "=R[-1]C+TIMEVALUE(""0:30"")"
    End With
End Sub

