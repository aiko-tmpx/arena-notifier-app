--[[
    AikoArenaNotifier - World of Warcraft Companion Addon
    Renders a solid 5x5 magenta square (#FF00FF) at top-left screen (0, 0)
    when an arena or Solo Shuffle queue pops.
--]]

local ADDON_NAME = "AikoArenaNotifier"
local isTestMode = false
local testTimer = nil

-- Create top-left 5x5 marker frame
local markerFrame = CreateFrame("Frame", "AikoArenaMarkerFrame", UIParent)
markerFrame:SetSize(5, 5)
markerFrame:SetPoint("TOPLEFT", UIParent, "TOPLEFT", 0, 0)
markerFrame:SetFrameStrata("TOOLTIP") -- Ensures top visual layer
markerFrame:EnableMouse(false)

local texture = markerFrame:CreateTexture(nil, "BACKGROUND")
texture:SetAllPoints(markerFrame)
texture:SetColorTexture(1.0, 0.0, 1.0, 1.0) -- Pure Magenta #FF00FF (RGB: 255, 0, 255)
markerFrame.texture = texture
markerFrame:Hide()

-- Helper to check if any battlefield or LFG queue pop is active
local function IsQueuePopActive()
    -- 1. Check PvP Battlefields & Arenas
    local maxBattlefields = (GetMaxBattlefieldID and GetMaxBattlefieldID()) or 5
    for i = 1, maxBattlefields do
        local status = GetBattlefieldStatus(i)
        if status == "confirm" then
            return true
        end
    end

    -- 2. Check PVPReadyDialog frame visibility
    if PVPReadyDialog and PVPReadyDialog:IsShown() then
        return true
    end

    -- 3. Check LFG / Dungeon / Solo Shuffle proposal frame visibility
    if LFGDungeonReadyDialog and LFGDungeonReadyDialog:IsShown() then
        return true
    end

    return false
end

-- Update marker visibility based on game state
local function UpdateMarkerState()
    if isTestMode then
        markerFrame:Show()
        return
    end

    if IsQueuePopActive() then
        markerFrame:Show()
    else
        markerFrame:Hide()
    end
end

-- Event listener
local eventFrame = CreateFrame("Frame")
eventFrame:RegisterEvent("PLAYER_ENTERING_WORLD")
eventFrame:RegisterEvent("UPDATE_BATTLEFIELD_STATUS")
eventFrame:RegisterEvent("PVP_BATTLEGROUND_CONFIRM_ENTRY")
eventFrame:RegisterEvent("LFG_PROPOSAL_SHOW")
eventFrame:RegisterEvent("LFG_PROPOSAL_FAILED")
eventFrame:RegisterEvent("LFG_PROPOSAL_SUCCEEDED")

eventFrame:SetScript("OnEvent", function(self, event, ...)
    UpdateMarkerState()
end)

-- Hook dialog show/hide for instant response
if PVPReadyDialog then
    PVPReadyDialog:HookScript("OnShow", UpdateMarkerState)
    PVPReadyDialog:HookScript("OnHide", UpdateMarkerState)
end

if LFGDungeonReadyDialog then
    LFGDungeonReadyDialog:HookScript("OnShow", UpdateMarkerState)
    LFGDungeonReadyDialog:HookScript("OnHide", UpdateMarkerState)
end

-- Slash commands
SLASH_AIKOARENA1 = "/aiko"
SlashCmdList["AIKOARENA"] = function(msg)
    local cmd = string.lower(string.trim and string.trim(msg) or msg:match("^%s*(.-)%s*$"))

    if cmd == "test" then
        isTestMode = true
        markerFrame:Show()
        print("|cffFF00FF[AikoArenaNotifier]|r Test marker shown at top-left (0, 0) for 6 seconds...")

        if C_Timer and C_Timer.After then
            C_Timer.After(6, function()
                isTestMode = false
                UpdateMarkerState()
                print("|cffFF00FF[AikoArenaNotifier]|r Test marker hidden.")
            end)
        end
    elseif cmd == "show" then
        isTestMode = true
        markerFrame:Show()
        print("|cffFF00FF[AikoArenaNotifier]|r Marker forced ON.")
    elseif cmd == "hide" then
        isTestMode = false
        markerFrame:Hide()
        print("|cffFF00FF[AikoArenaNotifier]|r Marker forced OFF.")
    else
        print("|cffFF00FF[AikoArenaNotifier]|r Commands:")
        print("  |cff00FFFF/aiko test|r - Shows 5x5 magenta square for 6 seconds to verify desktop scanner.")
        print("  |cff00FFFF/aiko show|r - Forces marker visible.")
        print("  |cff00FFFF/aiko hide|r - Forces marker hidden.")
    end
end
