import { useCallback } from 'react'
import {
  getPlaygroundSessionAPI,
  getAllPlaygroundSessionsAPI
} from '@/api/playground'
import { usePlaygroundStore } from '../store'
import { toast } from 'sonner'
import {
  PlaygroundChatMessage,
  ToolCall,
  ReasoningMessage,
  ChatEntry
} from '@/types/playground'

interface SessionResponse {
  session_id: string
  agent_id: string
  user_id: string | null
  memory?: {
    runs?: ChatEntry[]
    chats?: ChatEntry[]
  }
  runs?: {
    message: {
      role: string
      content: string
      created_at: number
    }
    response: {
      content: string
      created_at: number
      tools?: ToolCall[]
      extra_data?: any
      images?: any[]
      videos?: any[]
      audio?: any
      response_audio?: any
    }
  }[]
  agent_data: Record<string, unknown>
}

const useSessionLoader = () => {
  const setMessages = usePlaygroundStore((state) => state.setMessages)
  const selectedEndpoint = usePlaygroundStore((state) => state.selectedEndpoint)
  const setIsSessionsLoading = usePlaygroundStore(
    (state) => state.setIsSessionsLoading
  )
  const setSessionsData = usePlaygroundStore((state) => state.setSessionsData)

  const getSessions = useCallback(
    async (agentId: string) => {
      if (!agentId || !selectedEndpoint) return
      try {
        setIsSessionsLoading(true)
        const sessions = await getAllPlaygroundSessionsAPI(
          selectedEndpoint,
          agentId
        )
        setSessionsData(sessions)
      } catch {
        toast.error('Error loading sessions')
      } finally {
        setIsSessionsLoading(false)
      }
    },
    [selectedEndpoint, setSessionsData, setIsSessionsLoading]
  )

  const getSession = useCallback(
    async (sessionId: string, agentId: string) => {
      if (!sessionId || !agentId || !selectedEndpoint) {
        return null
      }

      try {
        console.log(`Loading session ${sessionId} for agent ${agentId}`)
        
        // Clear messages before loading new ones
        setMessages([])
        
        const response = await getPlaygroundSessionAPI(
          selectedEndpoint,
          agentId,
          sessionId
        ) as SessionResponse

        console.log('Session API response received')

        if (!response) {
          console.error('Session API returned empty response')
          return null
        }

        let processedMessages: PlaygroundChatMessage[] = []

        // First try to extract messages from the "runs" array in the root of the response
        if (response.runs && Array.isArray(response.runs)) {
          console.log('Found runs in root of response:', response.runs.length)
          
          processedMessages = response.runs.flatMap((run) => {
            const messages: PlaygroundChatMessage[] = []
            
            // Process user message
            if (run.message) {
              messages.push({
                role: 'user',
                content: run.message.content || '',
                created_at: run.message.created_at
              })
            }
            
            // Process agent response
            if (run.response) {
              // Process any tool calls
              const toolCalls = run.response.tools || []
              
              messages.push({
                role: 'agent',
                content: (typeof run.response.content === 'string') 
                  ? run.response.content 
                  : JSON.stringify(run.response.content) || '',
                tool_calls: toolCalls.length > 0 ? toolCalls : undefined,
                extra_data: run.response.extra_data,
                images: run.response.images,
                videos: run.response.videos,
                audio: run.response.audio,
                response_audio: run.response.response_audio,
                created_at: run.response.created_at
              })
            }
            
            return messages
          })
        } 
        // Fallback to the original memory.runs path
        else if (response.memory && (response.memory.runs || response.memory.chats)) {
          console.log('Falling back to memory.runs structure')
          
          const sessionHistory = response.memory.runs || response.memory.chats

          if (sessionHistory && Array.isArray(sessionHistory)) {
            processedMessages = sessionHistory.flatMap((run) => {
              const filteredMessages: PlaygroundChatMessage[] = []

              if (run.message) {
                filteredMessages.push({
                  role: 'user',
                  content: run.message.content || '',
                  created_at: run.message.created_at
                })
              }

              if (run.response) {
                const toolCalls = [
                  ...(run.response.tools || []),
                  ...((run.response.extra_data?.reasoning_messages || []).reduce(
                    (acc: ToolCall[], msg: ReasoningMessage) => {
                      if (msg.role === 'tool') {
                        acc.push({
                          role: msg.role,
                          content: msg.content,
                          tool_call_id: msg.tool_call_id || '',
                          tool_name: msg.tool_name || '',
                          tool_args: msg.tool_args || {},
                          tool_call_error: msg.tool_call_error || false,
                          metrics: msg.metrics || { time: 0 },
                          created_at:
                            msg.created_at || Math.floor(Date.now() / 1000)
                        })
                      }
                      return acc
                    },
                    []
                  ))
                ]

                filteredMessages.push({
                  role: 'agent',
                  content: (typeof run.response.content === 'string') 
                    ? run.response.content 
                    : JSON.stringify(run.response.content) || '',
                  tool_calls: toolCalls.length > 0 ? toolCalls : undefined,
                  extra_data: run.response.extra_data,
                  images: run.response.images,
                  videos: run.response.videos,
                  audio: run.response.audio,
                  response_audio: run.response.response_audio,
                  created_at: run.response.created_at
                })
              }
              return filteredMessages
            })
          }
        }

        // Process any content arrays
        const finalMessages = processedMessages.map(
          (message: PlaygroundChatMessage) => {
            if (Array.isArray(message.content)) {
              const textContent = message.content
                .filter((item: { type: string }) => item.type === 'text')
                .map((item) => item.text)
                .join(' ')

              return {
                ...message,
                content: textContent
              }
            }
            return message
          }
        )

        console.log('Processed messages:', finalMessages.length)
        
        if (finalMessages.length > 0) {
          // Set messages with a small delay to ensure state updates properly
          setTimeout(() => {
            setMessages(finalMessages)
            console.log('Messages set in store:', finalMessages.length)
          }, 10)
          
          return finalMessages
        } else {
          console.error('No messages found in session response')
          toast.error('No messages found in this session')
          return null
        }
      } catch (error) {
        console.error('Error loading session:', error)
        toast.error('Error loading session messages')
        return null
      }
    },
    [selectedEndpoint, setMessages]
  )

  return { getSession, getSessions }
}

export default useSessionLoader
