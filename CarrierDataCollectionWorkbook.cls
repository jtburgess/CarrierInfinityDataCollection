VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "ThisWorkbook"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True
' Workbook_Open MUST go in the Workbook Module
Sub Workbook_Open()
    Call InitShortcutKeys
End Sub

' assign macros their ctl-shift keyboard shortcuts
' and tell the user what they are
' Note. This doesn't do all of the validation done in ValidateChoreEnvironment
Sub InitShortcutKeys()
    Dim macroNames As Variant
    Dim macroKeys As Variant
    Dim msg As String
    Dim i As Long
    
    macroNames = Array("NextNonZeroInColB", "InsertMissingRow")
    macroKeys = Array("N", "I")
    
    For i = LBound(macroNames) To UBound(macroNames)
        ' '^' means CTL, '+' means SHIFT
        Application.OnKey "^+" & macroKeys(i), macroNames(i)
        msg = msg & "¥ " & "ctl-shift-" & macroKeys(i) & " => " & macroNames(i) & vbCrLf
    Next i
    MsgBox msg, vbOKOnly, "CarrierInfinity Macro Shortcuts"

End Sub

